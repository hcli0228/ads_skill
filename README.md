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

## ⚙️ 详细配置指南 (Step-by-Step Setup Guide)

### 步骤 1：获取 NASA ADS API Token

使用该工具需要先申请一个免费的 NASA ADS Developer API Token：
1. 访问并注册/登录 NASA ADS：[https://ui.adsabs.harvard.edu/](https://ui.adsabs.harvard.edu/)
2. 进入用户设置中的 API Token 页面：[https://ui.adsabs.harvard.edu/user/settings/token](https://ui.adsabs.harvard.edu/user/settings/token)
3. 点击 **"Generate a new token"** 按钮，复制生成的 40 位密钥字符串。

---

### 步骤 2：安装工具包

推荐在 Python 3.9+ 虚拟环境中进行安装：

```bash
# 1. 克隆代码仓库
git clone https://github.com/hcli0228/ads_skill.git
cd ads_skill

# 2. 安装项目与依赖（可编辑模式）
pip install -e .

# 或者直接安装 requirements
pip install -r requirements.txt
```

---

### 步骤 3：配置 API Token（四种灵活方式）

工具包按以下优先级自动识别并加载您的 API Token：

#### 方式一：使用 `.env` 文件（最推荐，项目内持久化）
复制模板文件并填入您的 Token：
```bash
cp .env.example .env
```
编辑 `.env` 文件：
```env
ADS_DEV_KEY=your_actual_token_here
```

#### 方式二：设置系统全局/用户环境变量
- **Linux / macOS**:
  ```bash
  # 临时生效
  export ADS_DEV_KEY="your_actual_token_here"

  # 永久生效（写入 ~/.bashrc 或 ~/.zshrc）
  echo 'export ADS_DEV_KEY="your_actual_token_here"' >> ~/.bashrc
  source ~/.bashrc
  ```
- **Windows (PowerShell)**:
  ```powershell
  # 当前会话临时生效
  $env:ADS_DEV_KEY="your_actual_token_here"

  # 用户级别永久生效
  [System.Environment]::SetEnvironmentVariable('ADS_DEV_KEY', 'your_actual_token_here', 'User')
  ```
- **Windows (CMD)**:
  ```cmd
  setx ADS_DEV_KEY "your_actual_token_here"
  ```

#### 方式三：命令行参数显式传入
```bash
ads-tool --token "your_actual_token_here" search "author:Hawking" --rows 5
```

#### 方式四：Python 代码中动态传入
```python
from ads_api import ADS

ads = ADS(token="your_actual_token_here")
```

---

### 步骤 4：验证安装与连通性测试

运行以下命令测试与 NASA ADS 服务器的连通性与检索功能：

```bash
ads-tool search "author:\"Hawking, S.\" \"black hole\"" --rows 3 --format table
```

若返回文献检索结果表格，则说明配置完全成功！

---

### 步骤 5：配置为 AI Agent 技能 (AI Agent Skill Integration)

如果您正在使用 **Antigravity**、**Claude Code**、**Cursor** 或其他 AI 编码助手：
1. 本仓库根目录下自带标准的 [`SKILL.md`](SKILL.md)。
2. 将本仓库克隆到 AI Agent 的技能发现目录（例如 `.gemini/skills/ads-database` 或当前工作区）。
3. 确保 `.env` 中已配置 `ADS_DEV_KEY`，AI Agent 即可自主识别并在对话中调用 ADS 检索文献、计算 $h$-index 与导出 BibTeX！

---

## 💻 命令行工具 CLI (`ads-tool` / `scripts/ads_tool.py`)

### 1. 文献检索 (`search`)
```bash
# 检索霍金被引最高的 5 篇黑洞论文，保存为 JSON
ads-tool search "author:\"Hawking, S.\" \"black hole\"" --rows 5 --sort "citation_count desc" --fl "bibcode,title,author,year,citation_count" --output hawking.json

# 以表格格式直观查看
ads-tool search "fast radio burst year:2024" --rows 5 --format table
```

### 2. 批量查询 (`bigquery`)
```bash
ads-tool bigquery --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --fl "bibcode,title,citation_count"
```

### 3. 统计指标计算 (`metrics`)
```bash
ads-tool metrics --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --summary
```

### 4. 引用导出 (`export`)
```bash
# 导出为 BibTeX
ads-tool export --bibcodes "1975CMaPh..43..199H" --format bibtex --output refs.bib

# 导出为 AASTeX (\bibitem)
ads-tool export --bibcodes "1975CMaPh..43..199H" --format aastex

# 自定义格式
ads-tool export --bibcodes "1975CMaPh..43..199H" --format custom --custom-format "%H (%Y): %T [%R]"
```

### 5. 共引文献推荐 (`recommend`)
```bash
ads-tool recommend --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --num 5
```

### 6. 文献库管理 (`library`)
```bash
# 列出文献库
ads-tool library list

# 创建文献库
ads-tool library create --name "Exoplanet Atmospheres" --desc "Key papers"
```

---

## 🐍 Python SDK API 使用示例

```python
from ads_api import ADS

# 初始化客户端（自动读取 .env 或系统环境变量中的 ADS_DEV_KEY）
ads = ADS()

# 1. 文献高级检索
results = ads.search.query(
    q='author:"Hawking" "black hole"',
    rows=5,
    sort="citation_count desc",
    fl=["bibcode", "title", "author", "year", "citation_count"]
)
for doc in results["docs"]:
    print(f"[{doc['citation_count']} 引用] {doc['title'][0]} ({doc['bibcode']})")

# 2. 计算文献计量指标 ($h$-index, 总引用, 去自引等)
metrics = ads.metrics.summarize_metrics(["1975CMaPh..43..199H", "1974Natur.248...30H"])
print(f"h-index: {metrics['h_index']}, 总引用: {metrics['total_citations']:,}")

# 3. 导出 BibTeX 参考文献
bibtex = ads.export.export(["1975CMaPh..43..199H"], format_name="bibtex")
print(bibtex)
```

---

## 🧪 自动化测试

运行完整测试套件：
```bash
pytest tests/ -v -p no:cacheprovider
```

---

## 📁 目录结构

```
ads_skill/
├── ads_api/                 # Python 核心服务库
│   ├── __init__.py          # 统一入口类 ADS
│   ├── config.py            # Token与环境配置
│   ├── client.py            # HTTP Client与错误处理
│   ├── search.py            # Solr 检索与 BigQuery
│   ├── metrics.py           # 学术统计与指标计算
│   ├── export.py            # 多格式引文导出
│   ├── libraries.py         # 文献库管理 (biblib)
│   ├── journals.py          # 期刊数据库
│   ├── resolver.py          # 外部资源解析
│   └── citation_helper.py   # 共引文献推荐
├── scripts/
│   └── ads_tool.py          # 统一 CLI 工具
├── tests/                   # 自动化测试用例
│   ├── test_ads_api.py
│   ├── test_cli.py
│   └── test_libraries.py
├── examples/                # 示例脚本
│   ├── quickstart_search.py
│   ├── metrics_analysis.py
│   └── literature_monitor.py
├── SKILL.md                 # Antigravity Agent Skill 规范文件
├── pyproject.toml           # 现代 PEP 517/621 标准打包配置
├── setup.py                 # 向后兼容安装入口
├── requirements.txt         # 依赖清单
├── LICENSE                  # MIT 开源协议
└── README.md                # 详细项目文档
```

---

## 📄 开源协议 (License)

本项目基于 [MIT License](LICENSE) 开源 - Copyright (c) 2026 hcli0228 (en-super@hotmail.com).
