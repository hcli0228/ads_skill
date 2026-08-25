"""
Literature Monitor Example: Monitoring recent papers and checking new citations
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ads_api import ADS

def monitor_topic(ads: ADS, topic_query: str, days_back: int = 30):
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    full_query = f"{topic_query} entdate:[{start_date} TO *]"
    
    print(f"Searching for new additions since {start_date} matching: {topic_query}")
    results = ads.search.query(
        q=full_query,
        rows=10,
        sort="date desc",
        fl=["bibcode", "title", "author", "pubdate", "citation_count", "doctype"]
    )
    
    print(f"Found {results['num_found']} recent papers:")
    for doc in results["docs"]:
        first_author = doc["author"][0] if doc.get("author") else "Unknown"
        title = doc["title"][0] if doc.get("title") else "No title"
        print(f"  - [{doc.get('pubdate')}] {first_author}: {title} ({doc['bibcode']})")

def main():
    ads = ADS()
    monitor_topic(ads, "gravitational wave optical counterpart", days_back=90)

if __name__ == "__main__":
    main()
