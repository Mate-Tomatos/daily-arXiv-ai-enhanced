# 🚀 daily-arXiv-ai-enhanced (Custom Fork)

> Forked from [dw-dengwei/daily-arXiv-ai-enhanced](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced) — Thanks to the original authors!

An automated daily arXiv paper tracker with AI-powered summarization, customized for specific research directions.

## 🎯 Research Focus

This fork is configured to track papers in the following research areas:

### Categories
`cs.CV` · `cs.CL` · `cs.RO` · `cs.AI` · `cs.LG`

### Research Directions

| Direction | Keywords |
|-----------|----------|
| **LLM Reasoning** | LLM reasoning, inference, step-by-step, logical/mathematical/commonsense/multi-step reasoning, self-consistency, RAG, RLHF, RLVR, reward model, tool use, planning, code generation, self-reflection |
| **Autonomous Driving & 3D** | autonomous driving, 3D object detection, 3D perception, point cloud, LiDAR, BEV, depth estimation, monocular/multi-view 3D, 3D tracking, trajectory prediction, end-to-end driving, sensor fusion, camera-LiDAR fusion, 3D semantic segmentation, 3D scene understanding |
| **4D Reconstruction** | 4D reconstruction, dynamic scene reconstruction, 4D scene, 4D/3D Gaussian splatting, 4D generation, scene flow, non-rigid reconstruction, dynamic/4D point cloud, novel view synthesis, 3D/multi-view reconstruction |

### Two-Layer Filtering

Papers are filtered through a two-layer mechanism:
1. **Required Terms (coarse filter):** Paper title or abstract must contain at least one of: `LLM`, `large language model`, `autonomous driving`, `feedback`
2. **Keywords (fine filter):** Papers must also match at least one keyword from the research directions above

## ✨ Features

- 🤖 **AI Summarization** — Daily paper crawling with DeepSeek-powered TL;DR summaries
- 🎯 **Zero Infrastructure** — Runs entirely on GitHub Actions + Pages, completely free
- 🔍 **Research Direction Filtering** — Papers are tagged and filterable by research keywords
- 💡 **Smart Reading** — Personalized highlighting, keyword/author filtering, text search
- 📱 **Cross-device** — Works on desktop and mobile

## 📖 Usage

**👉 [View Papers Online](https://Mate-Tomatos.github.io/daily-arXiv-ai-enhanced/)**

### Setup Your Own Instance

1. Fork this repo
2. Go to: Settings → Secrets and variables → Actions
3. Create repository **secrets**:
   - `OPENAI_API_KEY` — Your API key (e.g., DeepSeek API key)
   - `OPENAI_BASE_URL` — API base URL
4. Create repository **variables**:
   - `CATEGORIES` — e.g., `cs.CV, cs.CL, cs.RO, cs.AI, cs.LG`
   - `LANGUAGE` — e.g., `Chinese` or `English`
   - `MODEL_NAME` — e.g., `deepseek-chat`
   - `EMAIL` — Your email for git push
   - `NAME` — Your name for git push
5. Go to Actions → manually **Run workflow** to test
6. Set up GitHub Pages: Settings → Pages → Source: `Deploy from a branch`, Branch: `main`, `/(root)`

### Customizing Research Directions

Edit `daily_arxiv/config.yaml` to modify:
- `categories` — arXiv categories to crawl
- `required_terms` — First-layer coarse filter terms
- `keywords` — Second-layer fine filter keywords organized by research direction

## 🏗️ Architecture

```
daily_arxiv/          # Scrapy crawler + config
├── config.yaml       # Research direction configuration
├── daily_arxiv/
│   ├── spiders/arxiv.py    # arXiv spider
│   └── pipelines.py        # Two-layer keyword filtering pipeline
ai/                   # AI enhancement module
├── enhance.py        # DeepSeek summarization
├── structure.py      # Output structure
js/                   # Frontend
├── app.js            # Main application logic
├── data-config.js    # Data source configuration
```

## 🙏 Acknowledgement

This project is forked from [dw-dengwei/daily-arXiv-ai-enhanced](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced). All credit for the original design, architecture, and features goes to the original authors and contributors.
