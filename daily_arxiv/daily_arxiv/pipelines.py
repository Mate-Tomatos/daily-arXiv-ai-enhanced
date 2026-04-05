# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import json
import os
import re
import sys
import yaml
from datetime import datetime, timedelta
from scrapy.exceptions import DropItem


class DailyArxivPipeline:
    def __init__(self):
        self.page_size = 100
        self.client = arxiv.Client(self.page_size)
        self.required_terms, self.keywords = self._load_filter_config()

        # 预编译 required_terms 正则
        self.required_patterns = []
        if self.required_terms:
            for term in self.required_terms:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                self.required_patterns.append((term, pattern))
            print(f"[RequiredFilter] Loaded {len(self.required_terms)} required terms", file=sys.stderr)
        else:
            print("[RequiredFilter] No required_terms configured, skipping first-layer filter", file=sys.stderr)

        # 预编译 keywords 正则
        self.keyword_patterns = []
        if self.keywords:
            for kw in self.keywords:
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                self.keyword_patterns.append((kw, pattern))
            print(f"[KeywordFilter] Loaded {len(self.keywords)} keywords for filtering", file=sys.stderr)
        else:
            print("[KeywordFilter] No keywords configured, skipping second-layer filter", file=sys.stderr)

    def _load_filter_config(self):
        """从 config.yaml 加载 required_terms 和 keywords"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            arxiv_cfg = config.get('arxiv', {})

            required = arxiv_cfg.get('required_terms', [])
            if required:
                required = [t.strip() for t in required if t and t.strip()]
            else:
                required = []

            keywords = arxiv_cfg.get('keywords', [])
            if keywords:
                keywords = [kw.strip() for kw in keywords if kw and kw.strip()]
            else:
                keywords = []

            return required, keywords
        except Exception as e:
            print(f"[Filter] Failed to load config.yaml: {e}", file=sys.stderr)
            return [], []

    def _match_keywords(self, title, summary):
        """检查标题或摘要中是否包含至少一个关键词，返回匹配到的关键词列表"""
        if not self.keyword_patterns:
            return []  # 没有关键词配置，不过滤

        text = f"{title} {summary}"
        matched = []
        for kw, pattern in self.keyword_patterns:
            if pattern.search(text):
                matched.append(kw)
        return matched

    def process_item(self, item: dict, spider):
        item["pdf"] = f"https://arxiv.org/pdf/{item['id']}"
        item["abs"] = f"https://arxiv.org/abs/{item['id']}"
        search = arxiv.Search(
            id_list=[item["id"]],
        )
        paper = next(self.client.results(search))
        item["authors"] = [a.name for a in paper.authors]
        item["title"] = paper.title
        item["categories"] = paper.categories
        item["comment"] = paper.comment
        item["summary"] = paper.summary

        text = f"{item['title']} {item['summary']}"

        # 第一层过滤：required_terms（必须出现至少一个）
        if self.required_patterns:
            matched_required = []
            for term, pattern in self.required_patterns:
                if pattern.search(text):
                    matched_required.append(term)
            if not matched_required:
                raise DropItem(
                    f"[RequiredFilter] Dropped paper {item['id']} "
                    f"'{item['title'][:60]}...' - no required term match"
                )
            item["matched_required_terms"] = matched_required
            spider.logger.info(
                f"[RequiredFilter] Paper {item['id']} passed - matched required: {matched_required}"
            )

        # 第二层过滤：keywords（必须出现至少一个）
        if self.keyword_patterns:
            matched_kw = self._match_keywords(item["title"], item["summary"])
            if not matched_kw:
                raise DropItem(
                    f"[KeywordFilter] Dropped paper {item['id']} "
                    f"'{item['title'][:60]}...' - no keyword match"
                )
            item["matched_keywords"] = matched_kw
            spider.logger.info(
                f"[KeywordFilter] Kept paper {item['id']} - matched keywords: {matched_kw}"
            )

        return item
