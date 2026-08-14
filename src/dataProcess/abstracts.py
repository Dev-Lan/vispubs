import logging
import requests
import csv
import re
import time

INPUT_FILENAME = "./temp/new_papers.csv"
OUTPUT_FILENAME = "./temp/new_papers_abstract.csv"

# OpenAlex asks automated clients to identify themselves.
OPENALEX_USER_AGENT = "vispubs/1.0 (https://vispubs.com; mailto:devin@hms.harvard.edu)"


def strip_xml_tags(text):
    """Remove XML tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_abstract_from_doi_crossref(doi):
    logger = logging.getLogger("abstracts")
    base_url = "https://api.crossref.org/works/"
    url = f"{base_url}{doi}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        result = response.json()
        abstract = result["message"]["abstract"]
        abstract = strip_xml_tags(abstract)
        # the string "Abstract" is sometimes prepended to the abstract
        abstract = abstract.removeprefix("Abstract")
        return abstract
    except Exception as e:
        logger.error(f"Error fetching abstract for DOI {doi}: {e}")
        return None


def get_abstract_from_doi_semantic(doi):
    logger = logging.getLogger("abstracts")
    base_url = "https://api.semanticscholar.org/graph/v1/paper/"
    url = f"{base_url}{doi}?fields=title,abstract"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        result = response.json()
        abstract = result["abstract"]
        abstract = strip_xml_tags(abstract)
        return abstract
    except Exception as e:
        logger.error(f"Error fetching abstract for DOI {doi}: {e}")
        return None


def replace_special_chars(text):
    """Replace special characters in a string"""
    return (
        text.replace("‐", "-")
        .replace("‘", "'")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
    )


def reconstruct_inverted_abstract(inverted_index):
    """Rebuild plain text from OpenAlex's abstract_inverted_index.

    OpenAlex stores abstracts as {word: [positions]} rather than as text, so
    the words have to be placed back in order.
    """
    positions = []
    for word, indexes in inverted_index.items():
        for index in indexes:
            positions.append((index, word))
    positions.sort()
    return " ".join(word for _, word in positions)


def get_abstract_from_doi_openalex(doi):
    """Look up an abstract in OpenAlex, which covers some older material that
    Semantic Scholar and Crossref do not."""
    logger = logging.getLogger("abstracts")
    url = f"https://api.openalex.org/works/doi:{doi}"
    try:
        response = requests.get(url, headers={"User-Agent": OPENALEX_USER_AGENT})
        response.raise_for_status()
        inverted_index = response.json().get("abstract_inverted_index")
        if not inverted_index:
            return None
        return strip_xml_tags(reconstruct_inverted_abstract(inverted_index))
    except Exception as e:
        logger.error(f"Error fetching abstract for DOI {doi}: {e}")
        return None


def looks_like_abstract(text):
    """Reject responses that are technically non-empty but are not prose.

    A source can return a fragment rather than an abstract -- OpenAlex returned
    the single token "44" for one paper, which was stored as its abstract. An
    abstract is several sentences of prose, so requiring a handful of words and
    some letters filters that out while leaving genuinely short abstracts alone.
    """
    if text is None:
        return False
    stripped = text.strip()
    if len(stripped) < 40:
        return False
    if len(stripped.split()) < 8:
        return False
    return any(c.isalpha() for c in stripped)


def get_abstract_from_doi_with_source(doi):
    """Return (abstract, source), trying each source in turn.

    The source is reported so a backfill run can say where its recoveries came
    from rather than just how many there were. A source returning something that
    does not look like an abstract falls through to the next one.
    """
    logger = logging.getLogger("abstracts")
    # sleep for 2 seconds to avoid rate limiting
    time.sleep(2)
    for source, lookup in (
        ("semantic scholar", get_abstract_from_doi_semantic),
        ("crossref", get_abstract_from_doi_crossref),
        ("openalex", get_abstract_from_doi_openalex),
    ):
        abstract = lookup(doi)
        if abstract is None:
            continue
        if not looks_like_abstract(abstract):
            logger.warning(
                f"Discarding implausible abstract for {doi} from {source}: "
                f"{abstract.strip()[:60]!r}"
            )
            continue
        return replace_special_chars(abstract), source
    return None, None


def get_abstract_from_doi(doi):
    abstract, _ = get_abstract_from_doi_with_source(doi)
    return abstract


# 0 Conference
# 1 Year
# 2 Title
# 3 DOI
# 4 Abstract
# 5 AuthorNames-Deduped
# 6 Award
def add_abstracts(input_filename, output_filename):
    logger = logging.getLogger("abstracts")
    abstracts_found = 0
    abstracts_missing = 0
    with open(input_filename, "r") as source:
        reader = csv.reader(source)
        with open(output_filename, "w") as result:
            writer = csv.writer(result)
            for r in reader:
                logger.debug(f"{r[1]}, {r[3]}")
                if r[4] != "":
                    abstract = r[4]
                else:
                    abstract = get_abstract_from_doi(r[3])
                    if abstract is None:
                        logger.debug("\tskipped")
                        abstracts_missing += 1
                        abstract = ""
                    else:
                        logger.info(f"{r[1]}, {r[3]}")
                        logger.info("\tfound")
                        abstracts_found += 1
                writer.writerow((r[0], r[1], r[2], r[3], abstract, r[5], r[6]))
    logger.info(f"{abstracts_found}, of , {abstracts_missing + abstracts_found}")


if __name__ == "__main__":
    add_abstracts(INPUT_FILENAME, OUTPUT_FILENAME)
