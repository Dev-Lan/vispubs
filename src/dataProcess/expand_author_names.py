"""Expand abbreviated author first names to full names via Crossref and ORCID.

The Eurographics digital library publishes author names abbreviated to initials
for many papers ("Will, M."), so papers ingested from it by ingest_eurovis_26.py
start out with unusable given names. Initials cannot be matched against dblp
later and read poorly on author pages.

Full names are recoverable without scraping. Crossref's record for a DOI gives
each author's given name, family name, and usually an ORCID iD. Where Crossref
already spells the given name out, use it. Where it does not, the author's ORCID
record has their full name. That is the same information the publisher's author
popup links to, reached through two public JSON APIs instead.

Matching is conservative, following fix_early_access_authors.py: if Crossref's
author count differs from ours, or the family names do not line up positionally,
nothing is changed for that paper and it is reported for manual review.

Usage:
    python expand_author_names.py --year 2026 --dry-run
    python expand_author_names.py --year 2026

    # A single paper:
    python expand_author_names.py --doi 10.1111/cgf.70497
"""

import argparse
import http.client
import json
import logging
import os
import time
import unicodedata
import urllib.error
import urllib.request

import pandas as pd

EUROVIS_CSV = "./intermediate/eurovis.csv"
PAPERS_CSV = "../../public/data/papers.csv"
REPORT_FILE = "./temp/author_name_expansion_report.md"

CROSSREF_API = "https://api.crossref.org/works"
ORCID_API = "https://pub.orcid.org/v3.0"

# Crossref asks that automated clients identify themselves; doing so also routes
# requests to their faster "polite" pool.
CROSSREF_UA = "vispubs/1.0 (https://vispubs.com; mailto:devin@hms.harvard.edu)"

CROSSREF_DELAY = 0.3
ORCID_DELAY = 0.3

# "M." or "G. H." are initials; "Michael" is a name. Two characters after
# stripping periods is the cutoff, which keeps genuinely short names like "Yu".
MAX_INITIAL_LEN = 2


def looks_abbreviated(given):
    """True if a given name is initials rather than a spelled-out name."""
    if not given:
        return True
    parts = [p for p in given.replace(".", " ").split() if p]
    if not parts:
        return True
    # Abbreviated when every component is at most an initial's worth of letters.
    return all(len(p) <= MAX_INITIAL_LEN for p in parts)


# Crossref renders hyphenated surnames with U+2010 and friends rather than the
# ASCII hyphen the corpus uses. NFKD does not unify these, so "Abdul-Rahman" and
# "Abdul‐Rahman" would otherwise compare as different people.
DASHES = str.maketrans({c: "-" for c in "‐‑‒–—―−"})


def fold(text):
    """Casefold, strip accents, and unify dash variants, for comparing names."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.translate(DASHES).casefold().strip()


def fix_casing(name):
    """Title-case a name that arrived entirely lowercase.

    Some ORCID holders enter their name in lowercase ("weili zheng"). Only an
    all-lowercase name is touched, so genuine lowercase particles in names like
    "Tatiana von Landesberger" and deliberate capitalization like "d'Angelo"
    survive untouched.
    """
    if not name or not name.islower():
        return name
    return " ".join(part.capitalize() for part in name.split())


# dblp disambiguates authors who share a name with a trailing 4-digit ordinal.
DBLP_ORDINAL = __import__("re").compile(r"\s\d{4}$")


def name_key(name):
    """(first token, family token) for a corpus name, ignoring any dblp ordinal."""
    base = DBLP_ORDINAL.sub("", name).strip()
    parts = base.split()
    if len(parts) < 2:
        return None
    return fold(parts[0]), fold(parts[-1])


def build_corpus_index(papers_csv, exclude_dois):
    """Map (first, family) -> the corpus spellings of that author.

    Used to prefer a spelling already in the dataset over a differently
    abbreviated one, so "Stephen Kobourov" from ORCID becomes the existing
    "Stephen G. Kobourov" instead of forking that author into two names.
    """
    if not os.path.isfile(papers_csv):
        return {}
    df = pd.read_csv(papers_csv, dtype=str)
    excluded = {d.strip().lower() for d in exclude_dois}
    index = {}
    for doi, value in zip(df["DOI"].fillna(""), df["AuthorNames-Deduped"].fillna("")):
        if doi.strip().lower() in excluded:
            continue
        for name in split_authors(value):
            key = name_key(name)
            if key:
                index.setdefault(key, set()).add(name)
    return index


RETRIES = 3
RETRY_BACKOFF = 2.0

# A run touches a few hundred endpoints, so a single dropped connection must not
# end it. RemoteDisconnected and friends are OSError/HTTPException subclasses and
# are not covered by URLError, which is what made an early version die mid-run.
TRANSIENT = (
    urllib.error.URLError,
    http.client.HTTPException,
    OSError,
    TimeoutError,
)


def get_json(url, headers, timeout=45):
    """GET JSON, retrying transient network and 5xx failures."""
    logger = logging.getLogger("http")
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            # 404 and other 4xx are answers, not failures worth retrying.
            if e.code < 500:
                raise
            last = e
        except TRANSIENT as e:
            last = e
        if attempt < RETRIES:
            delay = RETRY_BACKOFF * attempt
            logger.warning(
                f"  retry {attempt}/{RETRIES - 1} in {delay:.0f}s ({last}) — {url}"
            )
            time.sleep(delay)
    raise last


def fetch_crossref_authors(doi):
    """Return [{given, family, orcid}] for a DOI, or None if unavailable."""
    try:
        data = get_json(
            f"{CROSSREF_API}/{doi}", {"User-Agent": CROSSREF_UA}
        )
    except TRANSIENT as e:
        logging.getLogger("crossref").warning(f"{doi}: {e}")
        return None
    authors = []
    for entry in data["message"].get("author") or []:
        orcid = (entry.get("ORCID") or "").rstrip("/").rsplit("/", 1)[-1]
        authors.append(
            {
                "given": (entry.get("given") or "").strip(),
                "family": (entry.get("family") or "").strip(),
                "orcid": orcid,
            }
        )
    return authors


def fetch_orcid_name(orcid, cache):
    """Return (given, family) from an ORCID record, or None."""
    if orcid in cache:
        return cache[orcid]
    try:
        data = get_json(
            f"{ORCID_API}/{orcid}/person", {"Accept": "application/json"}
        )
    except TRANSIENT as e:
        logging.getLogger("orcid").warning(f"{orcid}: {e}")
        cache[orcid] = None
        return None
    finally:
        time.sleep(ORCID_DELAY)

    name = data.get("name") or {}
    given = ((name.get("given-names") or {}).get("value") or "").strip()
    family = ((name.get("family-name") or {}).get("value") or "").strip()
    result = (given, family) if given else None
    cache[orcid] = result
    return result


def split_authors(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [n.strip() for n in str(value).split(";") if n.strip()]


def expand_paper(existing, crossref_authors, orcid_cache, logger, corpus=None):
    """Return (new_names, note) for one paper, or (None, reason) to skip it.

    Names are replaced positionally, so the author set and its order never
    change -- only the spelling of given names.
    """
    if crossref_authors is None:
        return None, "no Crossref record"
    if len(crossref_authors) != len(existing):
        return None, (
            f"author count differs: ours {len(existing)}, "
            f"Crossref {len(crossref_authors)}"
        )

    # Guard against a positional mismatch by checking family names align.
    for ours, theirs in zip(existing, crossref_authors):
        family = theirs["family"]
        if family and fold(family) not in fold(ours):
            return None, (
                f"family name mismatch at position "
                f"{existing.index(ours) + 1}: ours {ours!r}, "
                f"Crossref {theirs['given']} {family!r}"
            )

    new_names = []
    expanded = 0
    for ours, theirs in zip(existing, crossref_authors):
        given, family = theirs["given"], theirs["family"] or ours.split()[-1]

        if looks_abbreviated(given) and theirs["orcid"]:
            resolved = fetch_orcid_name(theirs["orcid"], orcid_cache)
            if resolved and not looks_abbreviated(resolved[0]):
                given = resolved[0]
                family = resolved[1] or family

        given, family = fix_casing(given), fix_casing(family)

        if looks_abbreviated(given):
            # Nothing better available; keep what we already had.
            new_names.append(ours)
            continue

        candidate = f"{given} {family}".strip()

        # Prefer a spelling already used in the corpus, so this author is not
        # forked into a second name that differs only in a middle initial.
        if corpus:
            key = name_key(candidate)
            matches = corpus.get(key) if key else None
            if matches and len(matches) == 1:
                existing_spelling = next(iter(matches))
                if existing_spelling != candidate:
                    logger.info(
                        f"    aligning {candidate!r} to existing "
                        f"{existing_spelling!r}"
                    )
                candidate = existing_spelling

        if candidate != ours:
            expanded += 1
        new_names.append(candidate)

    return new_names, f"{expanded} name(s) expanded"


def main():
    parser = argparse.ArgumentParser(
        description="Expand abbreviated author names via Crossref and ORCID"
    )
    parser.add_argument(
        "--csv",
        default=EUROVIS_CSV,
        help=f"intermediate CSV to correct (default: {EUROVIS_CSV})",
    )
    parser.add_argument("--year", help="restrict to this publication year")
    parser.add_argument("--doi", nargs="+", metavar="DOI", help="restrict to these DOIs")
    parser.add_argument(
        "--dry-run", action="store_true", help="report without writing"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("expand_author_names")

    df = pd.read_csv(args.csv, dtype=str)

    mask = pd.Series(True, index=df.index)
    if args.year:
        mask &= df["Year"].astype(str).str.strip() == str(args.year)
    if args.doi:
        wanted = {d.strip().lower() for d in args.doi}
        mask &= df["DOI"].fillna("").str.strip().str.lower().isin(wanted)
    if not mask.any():
        raise SystemExit("no rows matched the given --year/--doi filters")

    targets = df.index[mask]
    logger.info(f"{len(targets)} paper(s) selected from {args.csv}")

    # Index the rest of the corpus so resolved names can adopt a spelling that
    # already exists rather than introducing a near-duplicate.
    target_dois = [str(df.at[i, "DOI"]).strip() for i in targets]
    corpus = build_corpus_index(PAPERS_CSV, target_dois)
    logger.info(f"indexed {len(corpus)} author names from the rest of the corpus")

    orcid_cache = {}
    aligned = 0
    changed = papers_changed = 0
    skipped = []
    before_abbrev = after_abbrev = 0

    for idx in targets:
        row = df.loc[idx]
        existing = split_authors(row["AuthorNames-Deduped"])
        before_abbrev += sum(
            1 for n in existing if looks_abbreviated(" ".join(n.split()[:-1]))
        )

        authors = fetch_crossref_authors(str(row["DOI"]).strip())
        time.sleep(CROSSREF_DELAY)

        new_names, note = expand_paper(
            existing, authors, orcid_cache, logger, corpus=corpus
        )
        if new_names is None:
            skipped.append({"doi": row["DOI"], "title": row["Title"], "reason": note})
            after_abbrev += sum(
                1 for n in existing if looks_abbreviated(" ".join(n.split()[:-1]))
            )
            continue

        after_abbrev += sum(
            1 for n in new_names if looks_abbreviated(" ".join(n.split()[:-1]))
        )
        if new_names != existing:
            df.at[idx, "AuthorNames-Deduped"] = ";".join(new_names)
            papers_changed += 1
            changed += sum(1 for a, b in zip(existing, new_names) if a != b)
            logger.info(f"{row['DOI']}: {note}")

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Author name expansion report\n\n")
        f.write(f"**Papers selected:** {len(targets)}\n")
        f.write(f"**Papers changed:** {papers_changed}\n")
        f.write(f"**Names expanded:** {changed}\n")
        f.write(f"**Abbreviated before:** {before_abbrev}\n")
        f.write(f"**Abbreviated after:** {after_abbrev}\n")
        f.write(f"**Skipped:** {len(skipped)}\n\n")
        f.write("## Skipped — needs manual review\n\n")
        if not skipped:
            f.write("None.\n")
        for s in skipped:
            f.write(f"- **{s['title']}**\n  - DOI: `{s['doi']}`\n  - {s['reason']}\n")

    logger.info("")
    logger.info(f"papers selected:      {len(targets)}")
    logger.info(f"papers changed:       {papers_changed}")
    logger.info(f"names expanded:       {changed}")
    logger.info(f"abbreviated before:   {before_abbrev}")
    logger.info(f"abbreviated after:    {after_abbrev}")
    logger.info(f"skipped:              {len(skipped)}")
    logger.info(f"ORCID lookups:        {len(orcid_cache)}")
    logger.info(f"report:               {REPORT_FILE}")

    if args.dry_run:
        logger.info("")
        logger.info("--dry-run: nothing written")
        return

    df.to_csv(args.csv, index=False)
    logger.info(f"wrote {args.csv}")
    logger.info("")
    logger.info("Next: rebuild the published data, in this order —")
    logger.info("  combine() -> update_paper_link_flags() -> generate_parquet()")


if __name__ == "__main__":
    main()
