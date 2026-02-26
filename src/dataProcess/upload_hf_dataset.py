"""Upload papers.parquet to Hugging Face dataset repo with version tagging.

Usage:
    python upload_hf_dataset.py --version v2026.0-alpha --message "Initial alpha release"

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
HF_REPO_ID = "DevLan/vispubs"
VERSION_PATTERN = re.compile(r"^v\d{4}\.\d+(-[a-zA-Z][a-zA-Z0-9.]*)?$")

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


def get_existing_readme(api, repo_id):
    """Fetch the existing README.md from the HF repo, or return None."""
    try:
        path = api.hf_hub_download(repo_id=repo_id, filename="README.md", repo_type="dataset")
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def update_changelog(readme_content, version, message):
    """Append a new changelog entry to the README content."""
    today = date.today().isoformat()
    entry = f"### {version} ({today})\n\n- {message}\n\n"

    if readme_content and "## Changelog" in readme_content:
        # Insert after the Changelog heading
        parts = readme_content.split("## Changelog", 1)
        return parts[0] + "## Changelog\n\n" + entry + parts[1].lstrip("\n")
    else:
        # Use the template with the entry appended
        return DATASET_CARD_TEMPLATE + entry


def main():
    parser = argparse.ArgumentParser(description="Upload papers.parquet to Hugging Face")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v2026.0-alpha)")
    parser.add_argument("--message", required=True, help="Changelog entry describing changes")
    args = parser.parse_args()

    validate_version(args.version)

    if not os.path.isfile(PAPERS_PARQUET):
        print(f"Error: {PAPERS_PARQUET} not found. Run generate_parquet.py first.")
        sys.exit(1)

    api = HfApi()

    # Create repo if it doesn't exist
    api.create_repo(repo_id=HF_REPO_ID, repo_type="dataset", exist_ok=True)

    # Get existing README or use template
    existing_readme = get_existing_readme(api, HF_REPO_ID)
    readme_content = update_changelog(existing_readme, args.version, args.message)

    # Write temporary README
    readme_path = os.path.join(REPO_ROOT, ".hf_readme_tmp.md")
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # Upload parquet file
        print(f"Uploading papers.parquet to {HF_REPO_ID}...")
        api.upload_file(
            path_or_fileobj=PAPERS_PARQUET,
            path_in_repo="papers.parquet",
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            commit_message=f"{args.version}: {args.message}",
        )

        # Upload README
        print("Uploading dataset card...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            commit_message=f"{args.version}: Update dataset card",
        )

        # Create version tag
        print(f"Creating tag {args.version}...")
        api.create_tag(
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            tag=args.version,
            tag_message=args.message,
        )

        print(f"\nDone! Published {args.version} to https://huggingface.co/datasets/{HF_REPO_ID}")
    finally:
        if os.path.exists(readme_path):
            os.remove(readme_path)


if __name__ == "__main__":
    main()
