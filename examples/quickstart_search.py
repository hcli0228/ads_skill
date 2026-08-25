"""
Quickstart Example: Searching ADS Literature & Exporting BibTeX
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ads_api import ADS

def main():
    ads = ADS()
    print("=== 1. Searching for James Webb Space Telescope (JWST) early release papers ===")
    results = ads.search.query(
        q="JWST \"early release\" year:2022-2023",
        rows=5,
        sort="citation_count desc",
        fl=["bibcode", "title", "author", "year", "citation_count", "doi"]
    )
    
    print(f"Total Found: {results['num_found']}\n")
    bibcodes = []
    for doc in results["docs"]:
        bibcode = doc["bibcode"]
        bibcodes.append(bibcode)
        first_author = doc["author"][0] if doc.get("author") else "Unknown"
        title = doc["title"][0] if doc.get("title") else "No title"
        print(f"- [{doc.get('citation_count', 0)} cites] {first_author} ({doc.get('year')}): {title}")
        print(f"  Bibcode: {bibcode}\n")

    print("=== 2. Exporting Top Papers to BibTeX ===")
    bibtex = ads.export.export(bibcodes[:2], format_name="bibtex")
    print(bibtex)

if __name__ == "__main__":
    main()
