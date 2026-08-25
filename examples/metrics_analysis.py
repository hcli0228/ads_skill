"""
Bibliometric Evaluation Example: Calculating h-index, citations, and author metrics
"""
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ads_api import ADS

def main():
    ads = ADS()
    print("=== Calculating Bibliometrics for Stephen Hawking Landmark Papers ===")
    bibcodes = [
        "1975CMaPh..43..199H", # Particle creation by black holes
        "1974Natur.248...30H", # Black hole explosions?
        "1970RSPSA.314..529H", # The singularities of gravitational collapse and cosmology
        "1977PhRvD..15.2752G", # Action integrals and partition functions in quantum gravity
        "1983PhRvD..28.2960H", # Wave function of the Universe
    ]

    metrics = ads.metrics.summarize_metrics(bibcodes)
    print(f"Total Papers Analyzed: {metrics['total_papers']}")
    print(f"Total Citations:       {metrics['total_citations']:,}")
    print(f"Refereed Citations:    {metrics['refereed_citations']:,}")
    print(f"Distinct Citing Papers:{metrics['citing_papers']:,}")
    print(f"h-index:               {metrics['h_index']}")
    print(f"g-index:               {metrics['g_index']}")
    print(f"m-index:               {metrics['m_index']:.4f}")
    print(f"i10-index:             {metrics['i10_index']}")
    print(f"i100-index:            {metrics['i100_index']}")

if __name__ == "__main__":
    main()
