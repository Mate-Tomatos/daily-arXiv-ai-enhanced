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
        self.keywords = self._load_keywords()
        if self.keywords:
            # 预编译正则：对每个关键词构建 word-boundary 匹配（不区分大小写）
            # 对于含特殊字符的关键词（如 "3D"、"chain-of-thought"）使用精确匹配
            self.keyword_patterns = []
            for kw in self.keywords:
                # 转义正则特殊字符，然后用 \b 包裹做单词边界匹配
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                self.keyword_patterns.append((kw, pattern))
            print(f"[KeywordFilter] Loaded {len(self.keywords)} keywords for filtering", file=sys.stderr)
        else:
            self.keyword_patterns = []
            print("[KeywordFilter] No keywords configured, all papers will be kept", file=sys.stderr)

    def _load_keywords(self):
        """从 config.yaml 加载研究方向关键词列表"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            keywords = config.get('arxiv', {}).get('keywords', [])
            if keywords:
                return [kw.strip() for kw in keywords if kw and kw.strip()]
            return []
        except Exception as e:
            print(f"[KeywordFilter] Failed to load config.yaml: {e}", file=sys.stderr)
            return []

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

        # 关键词过滤：如果配置了关键词，则只保留标题或摘要中包含关键词的论文
        if self.keyword_patterns:
            matched = self._match_keywords(item["title"], item["summary"])
            if not matched:
                raise DropItem(
                    f"[KeywordFilter] Dropped paper {item['id']} "
                    f"'{item['title'][:60]}...' - no keyword match"
                )
            item["matched_keywords"] = matched
            spider.logger.info(
                f"[KeywordFilter] Kept paper {item['id']} - matched: {matched}"
            )

        return item
