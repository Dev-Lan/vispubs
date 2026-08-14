"""Fetch abstracts for papers that are missing one.

Abstracts are fetched once, during the ingest that first sees a paper. Anything
missed then stays missing, because the pipeline only ever looks at new papers.
This script goes back over papers that still have no abstract and tries again,
which is worthwhile after a new source is added to abstracts.py.

Corrections are written to the intermediate CSVs rather than to papers.csv, so
they survive the next pipeline run.

Usage:
    python backfill_abstracts.py --dry-run
    python backfill_abstracts.py
    python backfill_abstracts.py --year 2025
    python backfill_abstracts.py --doi 10.1111/cgf.70155
"""

import argparse
import csv
import logging
import os

from abstracts import get_abstract_from_doi_with_source

csv.field_size_limit(10**9)

INTERMEDIATE_FILES = [
    "./intermediate/VIS.csv",
    "./intermediate/eurovis.csv",
    "./intermediate/chi.csv",
]

PAPERS_CSV = "../../public/data/papers.csv"

# A DOI that never resolves anywhere; reported rather than counted as a failure.
PLACEHOLDER_DOI_PREFIX = "10.0000"


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def save(path, rows, fieldnames):
    # The intermediates are written by pandas elsewhere and so use bare LF.
    # csv.writer defaults to CRLF, which would rewrite every line of the file
    # and bury the real change in a whole-file diff.
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def published_dois():
    """DOIs currently on the site.

    The intermediates hold far more than gets published -- chi.csv carries every
    CHI paper, while only the visualization-relevant ones reach papers.csv. That
    matters here because filter_to_vis_papers matches keywords against the
    abstract as well as the title, so giving an unpublished CHI paper an
    abstract can pull it into the published set. Deciding which papers belong on
    the site is a separate question from filling in missing abstracts, so by
    default only papers already published are touched.
    """
    with open(PAPERS_CSV, newline="", encoding="utf-8") as f:
        return {r["DOI"].strip() for r in csv.DictReader(f) if r.get("DOI")}


def wanted(row, args, published):
    if (row.get("Abstract") or "").strip():
        return False
    if published is not None and (row.get("DOI") or "").strip() not in published:
        return False
    if args.year and str(row.get("Year", "")).strip() != str(args.year):
        return False
    if args.conference and row.get("Conference") != args.conference:
        return False
    if args.doi and row.get("DOI", "").strip().lower() not in {
        d.strip().lower() for d in args.doi
    }:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Fetch abstracts for papers that are missing one"
    )
    parser.add_argument("--year", help="only papers from this year")
    parser.add_argument("--conference", help="only papers from this venue")
    parser.add_argument("--doi", nargs="+", metavar="DOI", help="only these DOIs")
    parser.add_argument(
        "--dry-run", action="store_true", help="report without writing"
    )
    parser.add_argument(
        "--include-unpublished",
        action="store_true",
        help="also fill abstracts for intermediate rows that are not on the "
        "site. Note this can change which CHI papers the keyword filter "
        "selects, so review the resulting chi-filtered.csv.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("backfill_abstracts")

    published = None if args.include_unpublished else published_dois()
    if published is not None:
        logger.info(f"restricting to the {len(published)} papers on the site")

    found_by_source = {}
    still_missing = []
    unfixable = []
    total = 0

    for path in INTERMEDIATE_FILES:
        if not os.path.isfile(path):
            continue
        rows, fieldnames = load(path)
        targets = [r for r in rows if wanted(r, args, published)]
        if not targets:
            continue
        logger.info(f"{path}: {len(targets)} paper(s) without an abstract")
        changed = 0

        for row in targets:
            total += 1
            doi = (row.get("DOI") or "").strip()
            label = f"{row.get('Conference')} {row.get('Year')} — {row.get('Title', '')[:52]}"

            if not doi or doi.startswith(PLACEHOLDER_DOI_PREFIX):
                # No lookup can succeed without a real DOI.
                logger.info(f"  ⏭  placeholder DOI, cannot look up: {label}")
                unfixable.append((doi, row.get("Title", "")))
                continue

            abstract, source = get_abstract_from_doi_with_source(doi)
            if abstract:
                row["Abstract"] = abstract
                found_by_source[source] = found_by_source.get(source, 0) + 1
                changed += 1
                logger.info(f"  ✅ {source}: {label}")
            else:
                still_missing.append((doi, row.get("Title", "")))
                logger.info(f"  ❌ not found: {label}")

        if changed and not args.dry_run:
            save(path, rows, fieldnames)
            logger.info(f"  wrote {changed} abstract(s) to {path}")

    logger.info("")
    logger.info(f"papers checked:      {total}")
    for source, count in sorted(found_by_source.items()):
        logger.info(f"  found via {source}: {count}")
    logger.info(f"  recovered total:   {sum(found_by_source.values())}")
    logger.info(f"  still missing:     {len(still_missing)}")
    logger.info(f"  unfixable DOI:     {len(unfixable)}")

    if args.dry_run:
        logger.info("")
        logger.info("--dry-run: nothing written")
    else:
        logger.info("")
        logger.info("Next: rebuild the published data, in this order —")
        logger.info("  combine() -> update_paper_link_flags() -> generate_parquet()")


if __name__ == "__main__":
    main()
