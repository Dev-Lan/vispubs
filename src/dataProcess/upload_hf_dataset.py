"""Upload papers.parquet to Hugging Face dataset repo with version tagging.

Usage:
    Version and message resolved automatically -- the version from the tags
    already on the repo, the message from the newest changelog.md entry:
    python upload_hf_dataset.py --message-from-changelog

    Either can be given explicitly instead:
    python upload_hf_dataset.py --version v2026.4-alpha --message "Add EuroVis 2026"

    See what would be published without publishing:
    python upload_hf_dataset.py --message-from-changelog --dry-run

    Update only the dataset card (no data upload or version tag):
    python upload_hf_dataset.py --readme-only

Requirements:
    pip install huggingface_hub
    huggingface-cli login  (or set HF_TOKEN environment variable)
"""

import argparse
import os
import re
import sys
from datetime import date

from huggingface_hub import HfApi

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PAPERS_PARQUET = os.path.join(REPO_ROOT, "public", "data", "papers.parquet")
CHANGELOG = os.path.join(REPO_ROOT, "public", "data", "changelog.md")
HF_REPO_ID = "DevLan/vispubs"
VERSION_PATTERN = re.compile(r"^v\d{4}\.\d+(-[a-zA-Z][a-zA-Z0-9.]*)?$")

# Same shape as VERSION_PATTERN, but with the parts captured so existing tags can
# be compared to work out the next version.
VERSION_PARTS = re.compile(r"^v(\d{4})\.(\d+)(-[a-zA-Z][a-zA-Z0-9.]*)?$")

# Used when the repo has no tags at all to inherit a suffix from.
DEFAULT_PRERELEASE = "-alpha"

DATASET_CARD_TEMPLATE = """\
---
license: cc-by-4.0
task_categories:
  - text-classification
  - feature-extraction
language:
  - en
tags:
  - visualization
  - academic-papers
  - IEEE-VIS
  - EuroVis
  - CHI
pretty_name: VisPubs
size_categories:
  - 1K<n<10K
---

# VisPubs Dataset

A curated dataset of visualization research publications from IEEE VIS, EuroVis, and CHI conferences.

**Website:** [vispubs.com](https://vispubs.com)
**Source:** [github.com/Dev-Lan/vispubs](https://github.com/Dev-Lan/vispubs)

## Schema

| Column | Type | Description |
|--------|------|-------------|
| Conference | categorical | Conference venue (Vis, EuroVis, CHI) |
| Year | int | Publication year |
| Title | string | Paper title |
| DOI | string | Digital Object Identifier |
| Abstract | string | Paper abstract |
| AuthorNames-Deduped | list[string] | Author names (deduplicated) |
| Award | list[string] | Awards received (BP, HM, BCS, BA, TT) |
| Accessible | bool | Tagged for screen-reader accessibility |
| Early | bool | Early access publication |
| Resources | list[string] | Available resource types (P, V, C, PW, D, O) |
| ResourceLinks | list[struct] | Links for each resource: {name, url, icon} |

## Award Codes

- **BP** — Best Paper
- **HM** — Honorable Mention
- **BCS** — Best Case Study
- **BA** — Best Application
- **TT** — Test of Time

## Resource Codes

- **P** — Paper (preprint)
- **V** — Video
- **C** — Code
- **PW** — Project Website
- **D** — Data
- **O** — Other

## Usage

```bash
pip install datasets
```

Load the most recent version:

```python
from datasets import load_dataset
ds = load_dataset("DevLan/vispubs")
print(ds["train"].to_pandas().head())
```

Load a specific tagged version:

```python
from datasets import load_dataset
ds = load_dataset("DevLan/vispubs", revision="v2026.0-alpha")
print(ds["train"].to_pandas().head())
```

## Versioning

Versions follow `v{year}.{minor}` with optional prerelease suffixes:
- `alpha` — Early testing, schema may change
- `beta` — Near-stable, minor adjustments possible
- No suffix — Stable release

## Changelog

"""


def validate_version(version):
    if not VERSION_PATTERN.match(version):
        print(f"Error: Invalid version format '{version}'")
        print("Expected format: v{year}.{minor} or v{year}.{minor}-{prerelease}")
        print("Examples: v2026.0, v2026.1-alpha, v2026.2-beta")
        sys.exit(1)


def existing_versions(api, repo_id):
    """Return [(year, minor, suffix)] for every version tag on the repo."""
    refs = api.list_repo_refs(repo_id=repo_id, repo_type="dataset")
    parsed = []
    for tag in refs.tags:
        match = VERSION_PARTS.match(tag.name)
        if match:
            parsed.append(
                (int(match.group(1)), int(match.group(2)), match.group(3) or "")
            )
    return parsed


def next_version(api, repo_id, prerelease=None, stable=False):
    """Work out the next version from the tags already on the repo.

    The year is the current calendar year and the minor number is one past the
    highest already used in that year, so a new year restarts at 0 on its own.

    The prerelease suffix is inherited rather than dropped: forgetting to pass it
    would otherwise silently promote the dataset to a stable release. Pass
    --stable to drop it deliberately.

    Note the year here is the calendar year, which is not always the data cycle
    year -- a January run ingesting the previous VIS cycle is the case to watch.
    Pass --version explicitly for that.
    """
    year = date.today().year
    tags = existing_versions(api, repo_id)
    this_year = [t for t in tags if t[0] == year]

    if this_year:
        latest = max(this_year, key=lambda t: t[1])
        minor = latest[1] + 1
        inherited = latest[2]
    else:
        minor = 0
        # Carry the suffix across a year boundary from the newest tag overall.
        inherited = (
            max(tags, key=lambda t: (t[0], t[1]))[2] if tags else DEFAULT_PRERELEASE
        )

    if stable:
        suffix = ""
    elif prerelease:
        suffix = "-" + prerelease.lstrip("-")
    else:
        suffix = inherited

    return f"v{year}.{minor}{suffix}"


def latest_changelog_entry(path=CHANGELOG):
    """Return the newest changelog entry as a one-line release message.

    changelog.md is a reverse-chronological list of dated sections:

        ###### Aug 12, 2026

        - check 1702 papers from CHI[2026]
        - add newly found preprint links for 16 VIS 2025 papers

    The bullets of the first section become the message, so the release message
    is whatever was already written for the site changelog.
    """
    if not os.path.isfile(path):
        print(f"Error: {path} not found, cannot read a release message from it")
        sys.exit(1)

    bullets = []
    in_first_section = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("######"):
                if in_first_section:
                    break  # reached the next dated section
                in_first_section = True
                continue
            if in_first_section and line.strip().startswith("- "):
                bullets.append(line.strip()[2:].strip())

    if not bullets:
        print(f"Error: no bullet points found in the newest {path} entry")
        sys.exit(1)

    return "; ".join(bullets)


def get_existing_readme(api, repo_id):
    """Fetch the existing README.md from the HF repo, or return None."""
    try:
        path = api.hf_hub_download(repo_id=repo_id, filename="README.md", repo_type="dataset")
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def update_changelog(readme_content, version, message):
    """Always use the current template, preserving existing changelog entries."""
    today = date.today().isoformat()
    entry = f"### {version} ({today})\n\n- {message}\n\n"

    # Extract existing changelog entries from the remote README
    existing_entries = ""
    if readme_content and "## Changelog" in readme_content:
        existing_entries = readme_content.split("## Changelog", 1)[1].lstrip("\n")

    return DATASET_CARD_TEMPLATE + entry + existing_entries


def main():
    parser = argparse.ArgumentParser(description="Upload papers.parquet to Hugging Face")
    parser.add_argument(
        "--version",
        help="Version tag (e.g., v2026.4-alpha). Computed from the tags already "
        "on the repo when omitted.",
    )
    parser.add_argument("--message", help="Changelog entry describing changes")
    parser.add_argument(
        "--message-from-changelog",
        action="store_true",
        help="Use the newest entry in public/data/changelog.md as the message",
    )
    parser.add_argument(
        "--prerelease",
        help="Prerelease suffix for a computed version (e.g. beta). Inherited "
        "from the latest existing tag when omitted.",
    )
    parser.add_argument(
        "--stable",
        action="store_true",
        help="Drop the prerelease suffix from a computed version",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the version and message that would be published, then stop",
    )
    parser.add_argument("--readme-only", action="store_true", help="Only update the dataset card (no data upload or version tag)")
    args = parser.parse_args()

    if args.message and args.message_from_changelog:
        parser.error("pass either --message or --message-from-changelog, not both")
    if args.prerelease and args.stable:
        parser.error("--prerelease and --stable are mutually exclusive")

    message = args.message
    if not args.readme_only:
        if args.message_from_changelog:
            message = latest_changelog_entry()
        if not message:
            parser.error(
                "a message is required unless using --readme-only: pass "
                "--message or --message-from-changelog"
            )
        if args.version:
            validate_version(args.version)

        if not os.path.isfile(PAPERS_PARQUET):
            print(f"Error: {PAPERS_PARQUET} not found. Run generate_parquet.py first.")
            sys.exit(1)

    api = HfApi()

    # Create repo if it doesn't exist
    api.create_repo(repo_id=HF_REPO_ID, repo_type="dataset", exist_ok=True)

    # Resolve the version only after the repo is known to exist, since computing
    # it reads the repo's existing tags.
    version = args.version
    if not args.readme_only:
        already = {
            f"v{y}.{m}{s}" for y, m, s in existing_versions(api, HF_REPO_ID)
        }
        if not version:
            version = next_version(
                api, HF_REPO_ID, prerelease=args.prerelease, stable=args.stable
            )
            print(f"Computed next version: {version}")
        if version in already:
            # Re-tagging an existing version would publish different data under a
            # name someone may already have pinned.
            print(f"Error: tag {version} already exists on {HF_REPO_ID}")
            sys.exit(1)

        print(f"Version: {version}")
        print(f"Message: {message}")
        if args.dry_run:
            print("\n--dry-run: nothing published")
            return

    # Get existing README or use template
    existing_readme = get_existing_readme(api, HF_REPO_ID)
    if args.readme_only:
        # Preserve existing changelog, just refresh the template
        existing_entries = ""
        if existing_readme and "## Changelog" in existing_readme:
            existing_entries = existing_readme.split("## Changelog", 1)[1].lstrip("\n")
        readme_content = DATASET_CARD_TEMPLATE + existing_entries
    else:
        readme_content = update_changelog(existing_readme, version, message)

    # Write temporary README
    readme_path = os.path.join(REPO_ROOT, ".hf_readme_tmp.md")
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        if not args.readme_only:
            # Upload parquet file
            print(f"Uploading papers.parquet to {HF_REPO_ID}...")
            api.upload_file(
                path_or_fileobj=PAPERS_PARQUET,
                path_in_repo="papers.parquet",
                repo_id=HF_REPO_ID,
                repo_type="dataset",
                commit_message=f"{version}: {message}",
            )

        # Upload README
        print("Uploading dataset card...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            commit_message="Update dataset card" if args.readme_only else f"{version}: Update dataset card",
        )

        if not args.readme_only:
            # Create version tag
            print(f"Creating tag {version}...")
            api.create_tag(
                repo_id=HF_REPO_ID,
                repo_type="dataset",
                tag=version,
                tag_message=message,
            )

            print(f"\nDone! Published {version} to https://huggingface.co/datasets/{HF_REPO_ID}")
        else:
            print(f"\nDone! Updated dataset card at https://huggingface.co/datasets/{HF_REPO_ID}")
    finally:
        if os.path.exists(readme_path):
            os.remove(readme_path)


if __name__ == "__main__":
    main()
