"""Ingest EuroVis 2026 from the EG digital library as early access.

EuroVis 2026 papers are published in Computer Graphics Forum volume 45 issue 3,
but dblp had no CGF 2026 entries as of August 2026, so the normal dblp pipeline
cannot see them. The EG digital library has full metadata, so ingest from there.

The papers are flagged Early because diglib's author names are provisional: some
are spelled out, but many are abbreviated to "Last, F." form. Those cannot be
matched to dblp later and would look wrong on author pages, which is exactly what
the Early flag is for. Once dblp indexes CGF volume 45, generalize
fix_early_access_authors.py to accept the Comput. Graph. Forum venue and
intermediate/eurovis.csv, and let it replace these names with canonical ones.

Unlike the VIS early-access flow (ingest_vis_25.py), these papers already have
real DOIs, so no EARLY_ACCESS placeholder scheme is needed.

Usage:
    python ingest_eurovis_26.py --dry-run    # report what would be added
    python ingest_eurovis_26.py              # append to intermediate/eurovis.csv
"""

import argparse
import csv
import json
import logging
import os
import urllib.request

EUROVIS_CSV = "./intermediate/eurovis.csv"

DIGLIB_API = "https://diglib.eg.org/server/api"

# diglib returns 403 to unrecognized clients, so present a browser UA.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)

# Both EuroVis 2026 collections. Their DOI ranges do not overlap, so ingesting
# both produces no duplicates.
COLLECTIONS = {
    # DSpace name "45-Issue 3" -- the full-paper track.
    "full": "9a54a122-16ac-48a5-b7da-878247ecd160",
    # DSpace name "EuroVisSTAR2026" -- the State of the Art Report track. These
    # are EuroVis papers here, and additionally belong to the EuroVisSTAR
    # collection in public/data/collections/.
    "star": "8d108553-2624-408b-89fd-3a9b13d501a9",
}

CONFERENCE = "EuroVis"
YEAR = "2026"

# Awards are keyed by DOI, not title. The announced title of the Historians
# paper ("A Corpus-Based Taxonomy and Mixed-Methods Analysis") differs from the
# published one, so title matching would silently miss it.
AWARDS = {
    "10.1111/cgf.70474": "BP",  # Anchor Flow Maps
    "10.1111/cgf.70468": "HM",  # How Historians Use Visualization
    "10.1111/cgf.70443": "HM",  # Quantitative Metrics for Edge Bundling
    "10.1111/cgf.70432": "HM",  # Engagement vs. Understanding
}

FIELDNAMES = [
    "Conference",
    "Year",
    "Title",
    "DOI",
    "Abstract",
    "AuthorNames-Deduped",
    "Award",
    "Accessible",
    "Early",
]


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def fetch_collection(uuid):
    """Return the metadata dict for every item in a diglib collection."""
    url = (
        f"{DIGLIB_API}/discover/search/objects"
        f"?scope={uuid}&dsoType=item&size=200"
    )
    search_result = fetch_json(url)["_embedded"]["searchResult"]
    total = search_result["page"].get("totalElements", 0)
    objects = search_result["_embedded"]["objects"]
    if len(objects) != total:
        raise RuntimeError(
            f"collection {uuid}: got {len(objects)} of {total} items — "
            "the page size needs raising"
        )
    return [o["_embedded"]["indexableObject"]["metadata"] for o in objects]


def metadata_value(metadata, key):
    values = metadata.get(key) or []
    return values[0]["value"].strip() if values else ""


def metadata_values(metadata, key):
    return [v["value"].strip() for v in (metadata.get(key) or [])]


def to_first_last(name):
    """Convert diglib's "Last, First" author form to the corpus's "First Last".

    Names arrive inconsistently: "Stelter, Daniel" but also "Will, M.". Both are
    reordered the same way; the abbreviated ones stay abbreviated, which is part
    of why these papers are flagged Early.
    """
    if "," not in name:
        return name
    last, first = name.split(",", 1)
    last, first = last.strip(), first.strip()
    if not first:
        return last
    return f"{first} {last}"


def is_frontmatter(metadata):
    """Frontmatter entries carry neither authors nor an abstract.

    Matching on the title alone would be fragile, so require both to be absent.
    """
    has_authors = bool(metadata.get("dc.contributor.author"))
    has_abstract = bool(metadata_value(metadata, "dc.description.abstract"))
    return not has_authors and not has_abstract


def build_rows(logger):
    rows = []
    skipped_frontmatter = []

    for label, uuid in COLLECTIONS.items():
        items = fetch_collection(uuid)
        logger.info(f"{label}: fetched {len(items)} items from diglib")

        kept = 0
        for metadata in items:
            doi = metadata_value(metadata, "dc.identifier.doi")
            title = metadata_value(metadata, "dc.title")

            if is_frontmatter(metadata):
                skipped_frontmatter.append((doi, title))
                continue

            if not doi:
                raise RuntimeError(f"item has no DOI: {title!r}")

            authors = [
                to_first_last(name)
                for name in metadata_values(metadata, "dc.contributor.author")
            ]

            rows.append(
                {
                    "Conference": CONFERENCE,
                    "Year": YEAR,
                    "Title": title,
                    "DOI": doi,
                    "Abstract": metadata_value(metadata, "dc.description.abstract"),
                    "AuthorNames-Deduped": ";".join(authors),
                    "Award": AWARDS.get(doi, ""),
                    "Accessible": "",
                    "Early": "True",
                }
            )
            kept += 1
        logger.info(f"{label}: kept {kept} papers")

    for doi, title in skipped_frontmatter:
        logger.info(f"skipped frontmatter: {doi} — {title}")

    return rows


def existing_dois(path):
    if not os.path.isfile(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["DOI"].strip() for row in csv.DictReader(f) if row.get("DOI")}


def main():
    parser = argparse.ArgumentParser(
        description="Ingest EuroVis 2026 from the EG digital library"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would be added without writing",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("ingest_eurovis_26")

    rows = build_rows(logger)

    # Re-running must not duplicate rows already present.
    already = existing_dois(EUROVIS_CSV)
    new_rows = [r for r in rows if r["DOI"] not in already]
    duplicates = len(rows) - len(new_rows)

    awarded = [r for r in new_rows if r["Award"]]
    missing_awards = set(AWARDS) - {r["DOI"] for r in rows}

    logger.info("")
    logger.info(f"papers found:        {len(rows)}")
    logger.info(f"already present:     {duplicates}")
    logger.info(f"to add:              {len(new_rows)}")
    logger.info(f"awards applied:      {len(awarded)} of {len(AWARDS)}")
    for row in awarded:
        logger.info(f"  {row['Award']}  {row['DOI']}  {row['Title'][:58]}")
    if missing_awards:
        # An award DOI that matches nothing means the award list is wrong, which
        # would otherwise pass unnoticed.
        raise SystemExit(
            f"award DOIs not found among the ingested papers: {sorted(missing_awards)}"
        )

    abbreviated = sum(
        1
        for r in new_rows
        for name in r["AuthorNames-Deduped"].split(";")
        if len(name.split()) > 1 and len(name.split()[0].rstrip(".")) <= 2
    )
    logger.info(f"abbreviated first names (why these are Early): {abbreviated}")

    if args.dry_run:
        logger.info("")
        logger.info("--dry-run: nothing written")
        return

    if not new_rows:
        logger.info("nothing to add")
        return

    with open(EUROVIS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(new_rows)
    logger.info(f"appended {len(new_rows)} rows to {EUROVIS_CSV}")
    logger.info("")
    logger.info("Next: rebuild the published data, in this order —")
    logger.info("  combine() -> update_paper_link_flags() -> generate_parquet()")


if __name__ == "__main__":
    main()
