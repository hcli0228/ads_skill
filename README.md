# NASA ADS API Python Toolkit & Agent Skill (`ads-skill`)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NASA ADS](https://img.shields.io/badge/NASA%20ADS-API%20v1-orange.svg)](https://ui.adsabs.harvard.edu/)

A robust, full-featured Python toolkit and AI Agent Skill for the **NASA Astrophysics Data System (ADS)** Developer API. Designed for astronomers, researchers, bibliometricians, and autonomous AI coding agents (Antigravity, Claude Code, Cursor, OpenCodeInterpreter, etc.).

---

## 🌟 Key Features / 核心特性

- 🔍 **Advanced Solr Search**: Solr query syntax, field projection (`fl`), multi-parameter sorting, and pagination.
- 📦 **High-Throughput BigQuery**: Batch query metadata and citations for up to 2000 bibcodes in a single POST request.
- 📊 **Bibliometrics & Indicators (Metrics API)**: Calculate $h$-index, $g$-index, $m$-index, $i10$, $i100$, refereed vs. unrefereed citations, self-citations, and annual time series.
- 📑 **Citation Export (Export API)**: Export to BibTeX, AASTeX, MNRAS, RIS, EndNote, and custom string templates.
- 📚 **Library Synchronization (Libraries API)**: Create, read, update, delete, and share ADS collaborative libraries.
- 📖 **Journals Database (JournalsDB API)**: Look up journal metadata, publication history, ISSNs, and volume holdings.
- 🤖 **Co-Citation Recommendations (Citation Helper)**: Discover relevant missing papers using the "Friends of Friends" co-citation network.
- 🛡️ **Production-Ready Resilience**: Automatic Bearer token auth, rate-limit header tracking, exponential backoff retries, and comprehensive error handling.
- ⚡ **AI Agent Ready (Skill)**: Built-in `SKILL.md` compliant with Antigravity / Agent Skill specifications.

---

## 📦 Installation & Setup / 安装与配置

### 1. Installation

Install via pip:
```bash
git clone https://github.com/hcli0228/ads_skill.git
cd ads_skill
pip install -e .
```

### 2. Configure API Token

Obtain your free API token from the [NASA ADS API Settings](https://ui.adsabs.harvard.edu/user/settings/token).

Set your token via `.env` or environment variable:
```bash
# Option A: Copy .env.example to .env
cp .env.example .env
# Edit .env and set ADS_DEV_KEY=your_api_token_here

# Option B: Export environment variable
export ADS_DEV_KEY="your_api_token_here"
```

---

## 💻 CLI Usage (`ads-tool` / `scripts/ads_tool.py`)

### 1. Search Literature (`search`)
```bash
# Search top 5 cited black hole papers by Stephen Hawking
ads-tool search "author:\"Hawking, S.\" \"black hole\"" --rows 5 --sort "citation_count desc" --fl "bibcode,title,author,year,citation_count" --output hawking.json

# Table format output in terminal
ads-tool search "fast radio burst year:2024" --rows 5 --format table
```

### 2. Batch Bibcode Queries (`bigquery`)
```bash
ads-tool bigquery --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --fl "bibcode,title,citation_count"
```

### 3. Bibliometrics & Indicators (`metrics`)
```bash
ads-tool metrics --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --summary
```

### 4. Reference Export (`export`)
```bash
# Export to BibTeX
ads-tool export --bibcodes "1975CMaPh..43..199H" --format bibtex --output refs.bib

# Export to AASTeX (\bibitem)
ads-tool export --bibcodes "1975CMaPh..43..199H" --format aastex

# Custom format template
ads-tool export --bibcodes "1975CMaPh..43..199H" --format custom --custom-format "%H (%Y): %T [%R]"
```

### 5. Co-Citation Paper Recommendations (`recommend`)
```bash
ads-tool recommend --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --num 5
```

### 6. Manage ADS Libraries (`library`)
```bash
# List user libraries
ads-tool library list

# Create a new library
ads-tool library create --name "Exoplanet Atmospheres" --desc "Key papers"
```

---

## 🐍 Python SDK API Usage

```python
from ads_api import ADS

ads = ADS()

# 1. Literature Search
results = ads.search.query(
    q="author:Hawking",
    rows=5,
    fl=["bibcode", "title", "citation_count"]
)
for doc in results["docs"]:
    print(f"[{doc['citation_count']} cites] {doc['title'][0]} ({doc['bibcode']})")

# 2. Bibliometric Evaluation
metrics = ads.metrics.summarize_metrics(["1975CMaPh..43..199H", "1974Natur.248...30H"])
print(f"h-index: {metrics['h_index']}, Total citations: {metrics['total_citations']:,}")

# 3. Export to BibTeX
bibtex = ads.export.export(["1975CMaPh..43..199H"], format_name="bibtex")
print(bibtex)
```

---

## 🧪 Testing

Run test suite with pytest:
```bash
pytest tests/ -v -p no:cacheprovider
```

---

## 📁 Project Structure

```
ads_skill/
├── ads_api/                 # Core Python API package
│   ├── __init__.py          # Unified ADS client entrypoint
│   ├── config.py            # Token & environment resolver
│   ├── client.py            # HTTP client, auth & rate limiting
│   ├── search.py            # Solr search & BigQuery client
│   ├── metrics.py           # Bibliometric indices & metrics
│   ├── export.py            # Multi-format citation exporter
│   ├── libraries.py         # ADS libraries manager
│   ├── journals.py          # JournalsDB client
│   ├── resolver.py          # Fulltext / DOI / arXiv resolver
│   └── citation_helper.py   # Co-citation recommender
├── scripts/
│   └── ads_tool.py          # Unified CLI tool
├── tests/                   # Automated unit & integration tests
│   ├── test_ads_api.py
│   ├── test_cli.py
│   └── test_libraries.py
├── examples/                # Example workflows
│   ├── quickstart_search.py
│   ├── metrics_analysis.py
│   └── literature_monitor.py
├── .github/workflows/       # CI/CD pipeline
│   └── ci.yml
├── SKILL.md                 # Antigravity Agent Skill specification
├── pyproject.toml           # Modern PEP 517/621 packaging metadata
├── setup.py                 # Backward compatibility setup script
├── requirements.txt         # Dependency specification
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - Copyright (c) 2026 hcli0228 (en-super@hotmail.com).
