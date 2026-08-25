#!/usr/bin/env python
import os
import sys
import json
import argparse
from pathlib import Path
from typing import List

# Ensure ads_api package is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ads_api import ADS, ADSError
from tabulate import tabulate

def parse_bibcodes_arg(bibcodes_str: str = None, file_path: str = None) -> List[str]:
    bibs = []
    if bibcodes_str:
        bibs.extend([b.strip() for b in bibcodes_str.split(",") if b.strip()])
    if file_path:
        p = Path(file_path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        bibs.append(line)
    return list(dict.fromkeys(bibs)) # Deduplicate while preserving order

def save_output(data, output_path: str = None):
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                f.write(str(data))
        print(f"Results saved to: {output_path}")

def format_docs_table(docs: List[dict]) -> str:
    rows = []
    for d in docs:
        authors = d.get("author", [])
        first_author = authors[0] if authors else "Unknown"
        if len(authors) > 1:
            first_author += f" et al. ({len(authors)})"
        
        title = d.get("title", ["No Title"])
        title_str = title[0] if isinstance(title, list) and title else str(title)
        if len(title_str) > 60:
            title_str = title_str[:57] + "..."

        rows.append([
            d.get("bibcode", "-"),
            d.get("year", "-"),
            first_author,
            d.get("citation_count", 0),
            title_str
        ])
    return tabulate(rows, headers=["Bibcode", "Year", "Author", "Cites", "Title"], tablefmt="grid")

def cmd_search(ads: ADS, args):
    fl = [f.strip() for f in args.fl.split(",")] if args.fl else None
    results = ads.search.query(
        q=args.query,
        fl=fl,
        sort=args.sort,
        rows=args.rows,
        start=args.start,
        fq=args.fq,
        raw=args.raw
    )
    
    if args.format == "table" and not args.raw and "docs" in results:
        print(format_docs_table(results["docs"]))
        print(f"\nTotal Found: {results['num_found']}, Displaying: {results['rows_returned']}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    save_output(results, args.output)

def cmd_bigquery(ads: ADS, args):
    bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
    if not bibcodes:
        print("Error: No bibcodes provided. Use --bibcodes or --file.", file=sys.stderr)
        sys.exit(1)

    fl = [f.strip() for f in args.fl.split(",")] if args.fl else None
    results = ads.search.bigquery(
        bibcodes=bibcodes,
        q=args.query or "*:*",
        fl=fl,
        rows=args.rows,
        sort=args.sort
    )
    
    if args.format == "table" and "docs" in results:
        print(format_docs_table(results["docs"]))
        print(f"\nTotal Found: {results['num_found']}, Displaying: {results['rows_returned']}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    save_output(results, args.output)

def cmd_metrics(ads: ADS, args):
    bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
    if not bibcodes:
        print("Error: No bibcodes provided. Use --bibcodes or --file.", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        res = ads.metrics.summarize_metrics(bibcodes)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)
    else:
        types = [t.strip() for t in args.types.split(",")] if args.types else None
        res = ads.metrics.get_metrics(bibcodes, types=types)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)

def cmd_export(ads: ADS, args):
    bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
    if not bibcodes:
        print("Error: No bibcodes provided. Use --bibcodes or --file.", file=sys.stderr)
        sys.exit(1)

    exported_text = ads.export.export(
        bibcodes=bibcodes,
        format_name=args.format,
        sort=args.sort,
        custom_format=args.custom_format
    )
    print(exported_text)
    save_output(exported_text, args.output)

def cmd_library(ads: ADS, args):
    action = args.lib_action
    if action == "list":
        libs = ads.libraries.list_libraries(start=args.start, rows=args.rows)
        print(json.dumps(libs, ensure_ascii=False, indent=2))
        save_output(libs, args.output)
    elif action == "get":
        lib = ads.libraries.get_library(args.id)
        print(json.dumps(lib, ensure_ascii=False, indent=2))
        save_output(lib, args.output)
    elif action == "create":
        bibcodes = parse_bibcodes_arg(args.bibcodes, None)
        res = ads.libraries.create_library(name=args.name, description=args.desc, public=args.public, bibcodes=bibcodes)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)
    elif action == "add":
        bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
        res = ads.libraries.add_documents(args.id, bibcodes)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)
    elif action == "remove":
        bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
        res = ads.libraries.remove_documents(args.id, bibcodes)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)
    elif action == "delete":
        res = ads.libraries.delete_library(args.id)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        save_output(res, args.output)

def cmd_journal(ads: ADS, args):
    action = args.j_action
    if action == "summary":
        res = ads.journals.get_summary(args.bibstem)
    elif action == "search":
        res = ads.journals.search_journal(args.text)
    elif action == "issn":
        res = ads.journals.search_by_issn(args.issn)
    elif action == "holdings":
        res = ads.journals.get_holdings(args.bibstem, args.volume)
    else:
        res = {}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    save_output(res, args.output)

def cmd_recommend(ads: ADS, args):
    bibcodes = parse_bibcodes_arg(args.bibcodes, args.file)
    if not bibcodes:
        print("Error: No bibcodes provided.", file=sys.stderr)
        sys.exit(1)
    res = ads.citation_helper.get_recommendations(bibcodes, num_recommendations=args.num)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    save_output(res, args.output)

def cmd_resolve(ads: ADS, args):
    if args.type:
        res = ads.resolver.get_link_type(args.bibcode, args.type)
    else:
        res = ads.resolver.get_links(args.bibcode)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    save_output(res, args.output)

def main():
    parser = argparse.ArgumentParser(description="NASA ADS CLI Tool for AI Agents and Researchers")
    parser.add_argument("--token", help="Override ADS API Token")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    p_search = subparsers.add_parser("search", help="Execute Solr search queries against ADS")
    p_search.add_argument("query", help="Solr query string (e.g. 'author:Hawking year:1970-1980')")
    p_search.add_argument("--fl", help="Comma-separated field list (e.g. 'bibcode,title,author,citation_count')")
    p_search.add_argument("--sort", help="Sort order (e.g. 'citation_count desc')")
    p_search.add_argument("--rows", type=int, default=10, help="Number of rows to return")
    p_search.add_argument("--start", type=int, default=0, help="Start offset for pagination")
    p_search.add_argument("--fq", help="Filter query")
    p_search.add_argument("--format", choices=["json", "table"], default="json", help="Output format")
    p_search.add_argument("--raw", action="store_true", help="Return raw Solr JSON response")
    p_search.add_argument("--output", help="Save results to JSON/text file")

    # BigQuery
    p_bigquery = subparsers.add_parser("bigquery", help="Batch query up to 2000 bibcodes")
    p_bigquery.add_argument("--bibcodes", help="Comma-separated list of bibcodes")
    p_bigquery.add_argument("--file", help="Path to text file containing bibcodes")
    p_bigquery.add_argument("--query", default="*:*", help="Solr query filter")
    p_bigquery.add_argument("--fl", help="Comma-separated field list")
    p_bigquery.add_argument("--sort", help="Sort order")
    p_bigquery.add_argument("--rows", type=int, help="Number of rows")
    p_bigquery.add_argument("--format", choices=["json", "table"], default="json")
    p_bigquery.add_argument("--output", help="Save results to JSON file")

    # Metrics
    p_metrics = subparsers.add_parser("metrics", help="Calculate citation and publication metrics")
    p_metrics.add_argument("--bibcodes", help="Comma-separated list of bibcodes")
    p_metrics.add_argument("--file", help="Path to file containing bibcodes")
    p_metrics.add_argument("--types", help="Comma-separated metric types: basic,citations,indicators,histograms,timeseries")
    p_metrics.add_argument("--summary", action="store_true", help="Return clean key metrics summary")
    p_metrics.add_argument("--output", help="Save metrics to JSON file")

    # Export
    p_export = subparsers.add_parser("export", help="Export references in BibTeX, RIS, EndNote, etc.")
    p_export.add_argument("--bibcodes", help="Comma-separated list of bibcodes")
    p_export.add_argument("--file", help="Path to file containing bibcodes")
    p_export.add_argument("--format", default="bibtex", help="Format: bibtex, aastex, mnras, ris, endnote, custom, etc.")
    p_export.add_argument("--sort", help="Sort order")
    p_export.add_argument("--custom-format", help="Custom format string template")
    p_export.add_argument("--output", help="Save exported text to file (e.g. references.bib)")

    # Library
    p_lib = subparsers.add_parser("library", help="Manage ADS user libraries")
    lib_sub = p_lib.add_subparsers(dest="lib_action", required=True)
    
    p_lib_list = lib_sub.add_parser("list", help="List libraries")
    p_lib_list.add_argument("--start", type=int, default=0)
    p_lib_list.add_argument("--rows", type=int, default=20)
    p_lib_list.add_argument("--output", help="Save output to file")

    p_lib_get = lib_sub.add_parser("get", help="Get library contents")
    p_lib_get.add_argument("id", help="Library ID")
    p_lib_get.add_argument("--output", help="Save output to file")

    p_lib_create = lib_sub.add_parser("create", help="Create new library")
    p_lib_create.add_argument("--name", required=True, help="Library name")
    p_lib_create.add_argument("--desc", default="Created via ADS Tool", help="Description")
    p_lib_create.add_argument("--public", action="store_true", help="Make library public")
    p_lib_create.add_argument("--bibcodes", help="Initial comma-separated bibcodes")
    p_lib_create.add_argument("--output", help="Save output to file")

    p_lib_add = lib_sub.add_parser("add", help="Add bibcodes to library")
    p_lib_add.add_argument("id", help="Library ID")
    p_lib_add.add_argument("--bibcodes", help="Comma-separated bibcodes")
    p_lib_add.add_argument("--file", help="File with bibcodes")
    p_lib_add.add_argument("--output", help="Save output to file")

    p_lib_rm = lib_sub.add_parser("remove", help="Remove bibcodes from library")
    p_lib_rm.add_argument("id", help="Library ID")
    p_lib_rm.add_argument("--bibcodes", help="Comma-separated bibcodes")
    p_lib_rm.add_argument("--file", help="File with bibcodes")
    p_lib_rm.add_argument("--output", help="Save output to file")

    p_lib_del = lib_sub.add_parser("delete", help="Delete a library")
    p_lib_del.add_argument("id", help="Library ID")
    p_lib_del.add_argument("--output", help="Save output to file")

    # Journal
    p_journal = subparsers.add_parser("journal", help="Query JournalsDB")
    j_sub = p_journal.add_subparsers(dest="j_action", required=True)
    
    p_j_sum = j_sub.add_parser("summary", help="Get summary for bibstem")
    p_j_sum.add_argument("bibstem", help="Journal bibstem (e.g. ApJ, PASJ)")
    p_j_sum.add_argument("--output", help="Save output to file")

    p_j_search = j_sub.add_parser("search", help="Search journal by name")
    p_j_search.add_argument("text", help="Search string")
    p_j_search.add_argument("--output", help="Save output to file")

    p_j_issn = j_sub.add_parser("issn", help="Find bibstem by ISSN")
    p_j_issn.add_argument("issn", help="ISSN number")
    p_j_issn.add_argument("--output", help="Save output to file")

    p_j_hold = j_sub.add_parser("holdings", help="Get holdings")
    p_j_hold.add_argument("bibstem", help="Bibstem")
    p_j_hold.add_argument("volume", help="Volume")
    p_j_hold.add_argument("--output", help="Save output to file")

    # Recommend / Citation Helper
    p_rec = subparsers.add_parser("recommend", help="Recommend papers based on co-citations")
    p_rec.add_argument("--bibcodes", help="Comma-separated bibcodes")
    p_rec.add_argument("--file", help="Path to file containing bibcodes")
    p_rec.add_argument("--num", type=int, default=10, help="Number of recommendations")
    p_rec.add_argument("--output", help="Save output to file")

    # Resolve
    p_res = subparsers.add_parser("resolve", help="Resolve external links for a bibcode")
    p_res.add_argument("bibcode", help="Bibcode")
    p_res.add_argument("--type", help="Link type (abstract, article, preprint, etc.)")
    p_res.add_argument("--output", help="Save output to file")

    args = parser.parse_args()

    try:
        ads = ADS(token=args.token)
        if args.command == "search":
            cmd_search(ads, args)
        elif args.command == "bigquery":
            cmd_bigquery(ads, args)
        elif args.command == "metrics":
            cmd_metrics(ads, args)
        elif args.command == "export":
            cmd_export(ads, args)
        elif args.command == "library":
            cmd_library(ads, args)
        elif args.command == "journal":
            cmd_journal(ads, args)
        elif args.command == "recommend":
            cmd_recommend(ads, args)
        elif args.command == "resolve":
            cmd_resolve(ads, args)
    except ADSError as e:
        print(f"ADS Error ({e.status_code}): {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
