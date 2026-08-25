---
name: ads-database
description: >
  Query the NASA Astrophysics Data System (ADS) Developer API to search astronomy, astrophysics,
  and physics literature, calculate citation metrics and indicators (h-index, g-index, m-index),
  export citations (BibTeX, AASTeX, RIS, EndNote, custom formats), manage ADS libraries (biblib),
  inspect JournalsDB, resolve fulltext/arXiv/DOI links, and get co-citation paper recommendations.
---

# NASA ADS Database Skill

This skill enables AI agents and researchers to interact with the NASA Astrophysics Data System (ADS) Developer API. It supports programmatic searching, batch bibcode queries (BigQuery), bibliometric evaluations, citation export, library synchronization, journal lookup, and literature recommendations.

## Prerequisites & Configuration

1. **Python Environment**:
   - Python 3.9+ with required packages installed:
     ```bash
     pip install -e .
     # Or
     pip install -r requirements.txt
     ```
2. **API Token**:
   - Obtain your personal token from [NASA ADS API Settings](https://ui.adsabs.harvard.edu/user/settings/token).
   - Set it in your `.env` file or export as an environment variable:
     ```bash
     export ADS_DEV_KEY="your_api_token_here"
     ```

---

## Command-Line Tool Reference (`scripts/ads_tool.py` or `ads-tool`)

Agents and users can use `scripts/ads_tool.py` (or the installed `ads-tool` command) to query ADS and obtain clean JSON or formatted output.

### 1. Literature Search (`search`)
Execute Solr queries with field filtering, sorting, and pagination.

```bash
# Search top 5 cited papers on Hawking radiation
python scripts/ads_tool.py search "author:\"Hawking, S.\" \"black hole\"" --rows 5 --sort "citation_count desc" --fl "bibcode,title,author,year,citation_count" --output result.json

# Table format output for quick inspection
python scripts/ads_tool.py search "fast radio burst year:2023-2024" --rows 10 --format table
```

**Common Search Fields (`--fl`)**:
* `bibcode`: 19-character ADS identifier (e.g. `1975CMaPh..43..199H`)
* `title`: Title of the paper
* `author`: List of authors (Lastname, Firstname)
* `year`: Publication year
* `pubdate`: Publication date (YYYY-MM-DD or YYYY-MM)
* `citation_count`: Number of citations
* `read_count`: ADS read count
* `abstract`: Abstract text
* `doi`: Digital Object Identifier
* `doctype`: Document type (`article`, `eprint`, `inproceedings`, etc.)

---

### 2. Batch Bibcode Queries (`bigquery`)
Fetch metadata for up to 2000 bibcodes at once.

```bash
# Query list of bibcodes from CLI
python scripts/ads_tool.py bigquery --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --fl "bibcode,title,citation_count" --output bigquery_results.json

# Or load from a bibcodes text file
python scripts/ads_tool.py bigquery --file bibcodes.txt --output results.json
```

---

### 3. Bibliometrics & Impact Indicators (`metrics`)
Compute full publication, citation, and index metrics ($h$-index, $g$-index, $m$-index, $i10$, $i100$, tori index, self-citations).

```bash
# Get concise summary of metrics
python scripts/ads_tool.py metrics --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --summary --output metrics_summary.json

# Get full time series and histogram data
python scripts/ads_tool.py metrics --file my_papers.txt --output full_metrics.json
```

---

### 4. Citation & Reference Export (`export`)
Export bibliographic records into BibTeX, AASTeX, MNRAS, RIS, EndNote, or custom templates.

```bash
# Export to BibTeX file
python scripts/ads_tool.py export --bibcodes "1975CMaPh..43..199H" --format bibtex --output references.bib

# Export to AASTeX format
python scripts/ads_tool.py export --bibcodes "1975CMaPh..43..199H" --format aastex

# Export using custom formatting string
python scripts/ads_tool.py export --bibcodes "1975CMaPh..43..199H" --format custom --custom-format "%ZAUTHOR (%YEAR). %TITLE. %JOURNAL, %VOLUME, %PAGE"
```

---

### 5. Co-Citation Paper Recommendations (`recommend`)
Discover missing citations or related papers using ADS "friends of friends" co-citation analysis (requires at least 2 bibcodes).

```bash
python scripts/ads_tool.py recommend --bibcodes "1975CMaPh..43..199H,1974Natur.248...30H" --num 5 --output recs.json
```

---

### 6. ADS Libraries Management (`library`)
Manage remote ADS personal/collaborative libraries.

```bash
# List user libraries
python scripts/ads_tool.py library list

# Create a library
python scripts/ads_tool.py library create --name "Exoplanet Atmospheres" --desc "Key papers on transmission spectroscopy"

# Add papers to library
python scripts/ads_tool.py library add <library_id> --bibcodes "2017ApJ...848L..12A"

# Inspect library content
python scripts/ads_tool.py library get <library_id>
```

---

### 7. Journal Metadata & Holdings (`journal`)

```bash
# Get summary metadata for a journal
python scripts/ads_tool.py journal summary ApJ

# Search for journals matching name
python scripts/ads_tool.py journal search "Astrophysical"
```

---

### 8. Link & Identifier Resolver (`resolve`)

```bash
# Resolve external article/DOI/arXiv links for a bibcode
python scripts/ads_tool.py resolve "1975CMaPh..43..199H"
```

---

## Python API Usage in Custom Code

Agents and scripts can also directly import and use the `ads_api` package:

```python
from ads_api import ADS

ads = ADS()

# 1. Search
results = ads.search.query(q="author:Hawking", rows=5, fl=["bibcode", "title", "citation_count"])
for doc in results["docs"]:
    print(doc["bibcode"], doc["title"][0], doc["citation_count"])

# 2. Metrics
metrics = ads.metrics.summarize_metrics(["1975CMaPh..43..199H", "1974Natur.248...30H"])
print(f"h-index: {metrics['h_index']}, Total citations: {metrics['total_citations']}")

# 3. Export
bibtex_str = ads.export.export(["1975CMaPh..43..199H"], format_name="bibtex")
print(bibtex_str)
```
