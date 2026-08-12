"""Correct AuthorNames-Deduped for early-access papers against a dblp snapshot.

Early-access VIS papers are ingested from the conference program data (see
ingest_vis_25.py), which supplies author names that have never been through
dblp's author disambiguation. Those names carry no dblp suffixes, conflate
distinct people who share a name, and use spellings that differ from the rest of
the corpus. Once the papers are published for real and indexed by dblp, the
canonical names become available and should replace the program-supplied ones.

This script matches each early-access paper against a dblp snapshot by DOI, then
by normalized title, and replaces its author list with dblp's. It also clears the
Early flag on any paper whose placeholder DOI has since been replaced by a real
one (see update_doi.py).

Matching is deliberately conservative: if the dblp record's author count differs
from the existing row's, the change is NOT applied, because that signals a bad
match rather than a naming difference. Every paper that could not be matched
confidently is written to a report for manual review.

Usage:
    python fix_early_access_authors.py                 # apply corrections
    python fix_early_access_authors.py --dry-run       # report without writing

    # Use a pre-filtered subset instead of the full ~5GB dump:
    python fix_early_access_authors.py --dblp-xml ./temp/dblp_filtered.xml

Requires a dblp snapshot recent enough to contain the papers being corrected.
A stale snapshot produces a report full of unmatched papers rather than an error.
"""

import argparse
import logging
import os
import re

import pandas as pd
from lxml import etree

from parse_dblp_xml import get_doi, get_text, get_text_list

VIS_CSV = "./intermediate/VIS.csv"
DEFAULT_DBLP_XML = "./input/dblp.xml"
REPORT_FILE = "./temp/early_access_author_fix_report.md"
PAPERS_CSV = "../../public/data/papers.csv"
AUTHORS_CSV = "../../public/data/authors.csv"

# The venue early-access VIS papers are published in.
TVCG_JOURNAL = "IEEE Trans. Vis. Comput. Graph."

# Record-level elements in the dblp schema. Anything else is a child of one of
# these and must not be cleared independently of its parent.
RECORD_TAGS = frozenset(
    {
        "article",
        "inproceedings",
        "proceedings",
        "incollection",
        "book",
        "phdthesis",
        "mastersthesis",
        "www",
        "data",
    }
)

PLACEHOLDER_DOI_PREFIX = "EARLY_ACCESS"

# dblp appends a 4-digit ordinal to disambiguate authors who share a name.
DBLP_SUFFIX = re.compile(r"^(?P<base>.*?)\s(?P<ordinal>\d{4})$")


def normalize_title(title):
    """Collapse whitespace and case so titles can be compared across sources."""
    if pd.isna(title):
        return ""
    return " ".join(str(title).lower().split())


def split_authors(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [name.strip() for name in str(value).split(";") if name.strip()]


def is_early(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


def build_dblp_index(xml_path):
    """Stream a dblp snapshot, indexing TVCG articles by DOI and by title.

    Returns (by_doi, by_title). by_title maps a normalized title to a list of
    records, since a title can legitimately appear more than once (for example a
    journal version alongside a conference version).
    """
    logger = logging.getLogger("build_dblp_index")
    by_doi = {}
    by_title = {}

    # load_dtd resolves the HTML entities dblp uses in author names (&uuml; etc).
    # huge_tree lifts libxml2's default size limits for the full dump.
    context = etree.iterparse(
        xml_path, events=("end",), load_dtd=True, huge_tree=True
    )

    seen = 0
    for _, elem in context:
        # iterparse fires an end event for every element, including the children
        # of a record. Only record-level elements may be cleared — clearing a
        # child would destroy the parent's data before it is read. Every
        # record-level element must be cleared, not just the ones we keep, or the
        # whole ~5GB dump accumulates in memory.
        if elem.tag not in RECORD_TAGS:
            continue

        if elem.tag != "article":
            _clear(elem)
            continue

        seen += 1
        if seen % 500_000 == 0:
            logger.info(f"scanned {seen / 1_000_000:.1f}M articles")

        if get_text(elem, "journal") != TVCG_JOURNAL:
            _clear(elem)
            continue

        title = get_text(elem, "title") or ""
        if title.endswith("."):
            title = title[:-1]

        record = {
            "title": title,
            "doi": get_doi(elem),
            "authors": get_text_list(elem, "author"),
            "year": get_text(elem, "year"),
        }

        if record["doi"]:
            by_doi[record["doi"].lower()] = record
        by_title.setdefault(normalize_title(title), []).append(record)

        _clear(elem)

    logger.info(
        f"indexed {len(by_doi)} TVCG articles by DOI, "
        f"{len(by_title)} distinct titles"
    )
    return by_doi, by_title


def _clear(elem):
    """Release a parsed element and its already-processed siblings."""
    elem.clear()
    while elem.getprevious() is not None:
        del elem.getparent()[0]


def resolve(row, by_doi, by_title):
    """Find the dblp record for a paper row.

    Returns (record, how) where how is "doi" or "title", or (None, reason).
    """
    doi = str(row.get("DOI") or "").strip()
    if doi and not doi.startswith(PLACEHOLDER_DOI_PREFIX):
        record = by_doi.get(doi.lower())
        if record:
            return record, "doi"

    candidates = by_title.get(normalize_title(row.get("Title")), [])
    if len(candidates) == 1:
        return candidates[0], "title"
    if len(candidates) > 1:
        return None, f"ambiguous title ({len(candidates)} dblp records)"
    return None, "no dblp record found"


def fix_authors(vis_csv, xml_path, dry_run=False, dois=None, allow_count_change=()):
    """Correct author names for early-access papers, or for specific DOIs.

    dois restricts the work to those papers regardless of their Early flag, which
    is what makes a correction re-runnable after the flag has been cleared.

    allow_count_change lists DOIs where a differing author count has been
    reviewed by a human and should be applied. The default is to refuse, since an
    unexpected count usually means the match is wrong.
    """
    logger = logging.getLogger("fix_early_access_authors")
    allow_count_change = {d.strip().lower() for d in allow_count_change}

    df = pd.read_csv(vis_csv, dtype=str)
    if dois:
        wanted = {d.strip().lower() for d in dois}
        early_mask = df["DOI"].fillna("").str.strip().str.lower().isin(wanted)
        found = int(early_mask.sum())
        if found != len(wanted):
            missing = wanted - set(df["DOI"].fillna("").str.strip().str.lower())
            raise SystemExit(f"DOIs not found in {vis_csv}: {sorted(missing)}")
        logger.info(f"targeting {found} paper(s) by DOI")
    else:
        early_mask = df["Early"].apply(is_early)

    early_count = int(early_mask.sum())
    if early_count == 0:
        logger.info("No papers flagged Early — nothing to do.")
        return

    logger.info(f"{early_count} papers flagged Early in {vis_csv}")
    logger.info(f"Indexing {xml_path} (this reads the whole snapshot)...")
    by_doi, by_title = build_dblp_index(xml_path)

    matched_by = {"doi": 0, "title": 0}
    names_changed = 0
    early_cleared = 0
    unmatched = []
    mismatched = []

    for idx in df.index[early_mask]:
        row = df.loc[idx]
        existing = split_authors(row["AuthorNames-Deduped"])

        record, how = resolve(row, by_doi, by_title)
        if record is None:
            unmatched.append({"row": row, "reason": how})
        else:
            matched_by[how] += 1
            replacement = record["authors"]

            doi_key = str(row.get("DOI") or "").strip().lower()
            if (
                len(replacement) != len(existing)
                and doi_key not in allow_count_change
            ):
                # A differing author count usually means the match is wrong, not
                # that the names need updating. Refuse unless a human has
                # reviewed this specific paper and passed it in explicitly.
                mismatched.append(
                    {
                        "row": row,
                        "matched_via": how,
                        "existing": existing,
                        "replacement": replacement,
                    }
                )
            elif replacement != existing:
                if len(replacement) != len(existing):
                    logger.info(
                        f"applying reviewed author-count change for {doi_key}: "
                        f"{len(existing)} -> {len(replacement)} authors"
                    )
                df.at[idx, "AuthorNames-Deduped"] = ";".join(replacement)
                names_changed += 1

        # Independent of the author lookup: a paper that has acquired a real DOI
        # is no longer early access.
        doi = str(row.get("DOI") or "").strip()
        if doi and not doi.startswith(PLACEHOLDER_DOI_PREFIX):
            df.at[idx, "Early"] = ""
            early_cleared += 1

    write_report(unmatched, mismatched, early_count, matched_by, names_changed)

    if dry_run:
        logger.info("--dry-run: no files written")
    else:
        df.to_csv(vis_csv, index=False)
        logger.info(f"wrote {vis_csv}")

    logger.info("")
    logger.info(f"Early papers processed:     {early_count}")
    logger.info(f"  matched by DOI:           {matched_by['doi']}")
    logger.info(f"  matched by title:         {matched_by['title']}")
    logger.info(f"  unmatched:                {len(unmatched)}")
    logger.info(f"  author-count mismatches:  {len(mismatched)} (not applied)")
    logger.info(f"Author lists rewritten:     {names_changed}")
    logger.info(f"Early flags cleared:        {early_cleared}")
    logger.info(f"Report:                     {REPORT_FILE}")


def write_report(unmatched, mismatched, early_count, matched_by, names_changed):
    lines = [
        "# Early-access author correction report",
        "",
        f"**Early papers processed:** {early_count}",
        f"**Matched by DOI:** {matched_by['doi']}",
        f"**Matched by title:** {matched_by['title']}",
        f"**Author lists rewritten:** {names_changed}",
        f"**Unmatched:** {len(unmatched)}",
        f"**Author-count mismatches (not applied):** {len(mismatched)}",
        "",
    ]

    lines.append("## Author-count mismatches — needs manual review")
    lines.append("")
    if not mismatched:
        lines.append("None.")
    else:
        lines.append(
            "These papers matched a dblp record whose author count differs from "
            "ours. The match is suspect, so no change was applied."
        )
        lines.append("")
        for item in mismatched:
            row = item["row"]
            lines.append(f"- **{row['Title']}**")
            lines.append(f"  - DOI: `{row['DOI']}` (matched via {item['matched_via']})")
            lines.append(
                f"  - ours ({len(item['existing'])}): {'; '.join(item['existing'])}"
            )
            lines.append(
                f"  - dblp ({len(item['replacement'])}): "
                f"{'; '.join(item['replacement'])}"
            )
    lines.append("")

    lines.append("## Unmatched — no confident dblp record")
    lines.append("")
    if not unmatched:
        lines.append("None.")
    else:
        for item in unmatched:
            row = item["row"]
            lines.append(f"- **{row['Title']}**")
            lines.append(f"  - DOI: `{row['DOI']}`")
            lines.append(f"  - reason: {item['reason']}")
            lines.append(f"  - current authors: {row['AuthorNames-Deduped']}")
    lines.append("")

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def reconcile_authors_csv(papers_csv, authors_csv, dry_run=False):
    """Realign authors.csv names with the corrected corpus.

    authors.csv maps an author name to their homepage. The name is the only key,
    so a name that changed during correction silently orphans the homepage link.
    Where a stale name maps unambiguously onto exactly one corrected name, fix
    it; anything ambiguous is reported instead.
    """
    logger = logging.getLogger("reconcile_authors_csv")

    papers = pd.read_csv(papers_csv, dtype=str)
    corpus = set()
    for value in papers["AuthorNames-Deduped"]:
        corpus.update(split_authors(value))

    # Map an unsuffixed base name to the suffixed corpus names sharing it.
    by_base = {}
    for name in corpus:
        match = DBLP_SUFFIX.match(name)
        if match:
            by_base.setdefault(match.group("base"), []).append(name)

    authors = pd.read_csv(authors_csv, dtype=str)
    updated = 0
    ambiguous = []

    for idx, row in authors.iterrows():
        name = str(row["author"]).strip()
        if name in corpus:
            continue
        candidates = by_base.get(name, [])
        if len(candidates) == 1:
            logger.info(f"authors.csv: '{name}' -> '{candidates[0]}'")
            authors.at[idx, "author"] = candidates[0]
            updated += 1
        elif len(candidates) > 1:
            ambiguous.append((name, candidates))
        else:
            logger.warning(
                f"authors.csv: '{name}' matches no paper author — left as-is"
            )

    for name, candidates in ambiguous:
        logger.warning(
            f"authors.csv: '{name}' is ambiguous ({', '.join(candidates)}) "
            "— left as-is, fix by hand"
        )

    if updated and not dry_run:
        authors.to_csv(authors_csv, index=False)
        logger.info(f"wrote {authors_csv} ({updated} names realigned)")
    else:
        logger.info(f"authors.csv: {updated} names would be realigned")


def regenerate_published_data():
    """Rebuild the published CSV and Parquet files from the intermediates.

    Order matters. combine() blanks the Resources column for every row, so
    update_paper_link_flags() has to run afterwards to recompute it — that is the
    same order main.py uses. Running update_paper_link_flags() last also keeps the
    CRLF line endings papers.csv is committed with, since it writes via
    csv.writer while combine() writes via pandas; reversing them would rewrite
    every line of the file.
    """
    logger = logging.getLogger("regenerate")

    from combine import combine
    from generate_parquet import generate_parquet
    from update_paper_link_flags import update_paper_link_flags

    logger.info("combine: rebuilding papers.csv from intermediates")
    combine()
    logger.info("update_paper_link_flags: recomputing the Resources column")
    update_paper_link_flags()
    return generate_parquet


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    parser = argparse.ArgumentParser(
        description="Correct early-access author names against a dblp snapshot"
    )
    parser.add_argument(
        "--dblp-xml",
        default=DEFAULT_DBLP_XML,
        help=f"dblp snapshot to match against (default: {DEFAULT_DBLP_XML})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing any files",
    )
    parser.add_argument(
        "--authors-only",
        action="store_true",
        help="skip the paper correction and only realign authors.csv",
    )
    parser.add_argument(
        "--no-regen",
        action="store_true",
        help="correct the intermediate file only; skip rebuilding papers.csv "
        "and the Parquet files",
    )
    parser.add_argument(
        "--doi",
        nargs="+",
        metavar="DOI",
        help="correct only these papers, regardless of their Early flag. Use to "
        "re-run a correction after the flag has already been cleared.",
    )
    parser.add_argument(
        "--allow-author-count-change",
        nargs="+",
        default=[],
        metavar="DOI",
        help="apply dblp's author list for these DOIs even though its author "
        "count differs from ours. Only pass a DOI after reviewing it in the "
        "report — an unexpected count usually means a bad match.",
    )
    args = parser.parse_args()

    configure_logging()

    if not args.authors_only:
        if not os.path.isfile(args.dblp_xml):
            raise SystemExit(f"dblp snapshot not found: {args.dblp_xml}")
        fix_authors(
            VIS_CSV,
            args.dblp_xml,
            dry_run=args.dry_run,
            dois=args.doi,
            allow_count_change=args.allow_author_count_change,
        )

    if args.dry_run or args.no_regen:
        # papers.csv still holds the uncorrected names, so reconciling
        # authors.csv against it would compare with stale data.
        logging.getLogger("main").info(
            "skipping regeneration; authors.csv reconciliation runs in report-only "
            "mode against the existing papers.csv"
        )
        reconcile_authors_csv(PAPERS_CSV, AUTHORS_CSV, dry_run=True)
        return

    generate_parquet = regenerate_published_data()

    # Only now does papers.csv carry the corrected names, so this is the first
    # point at which a stale authors.csv entry can be detected.
    reconcile_authors_csv(PAPERS_CSV, AUTHORS_CSV, dry_run=False)

    # authors.csv may have just changed, so the Parquet files are generated last.
    generate_parquet()


if __name__ == "__main__":
    main()
