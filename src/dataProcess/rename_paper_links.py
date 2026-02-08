"""
rename_paper_links.py

Bulk rename paperLinks files using the DOI update map (doi_updates.csv).

Reads the Old_DOI -> New_DOI mapping and renames files under
public/data/paperLinks/ accordingly. For example:
  EARLY_ACCESS/14e8969b-...  ->  10.1109/TVCG.2025.3633830

The new DOI prefix directory (e.g. 10.1109/) is created if it doesn't exist.

Usage:
  python rename_paper_links.py
"""

import pandas as pd
import os
import shutil

DOI_MAP_FILENAME = "./temp/doi_updates.csv"
PAPER_LINKS_DIR = "../../public/data/paperLinks"


def rename_paper_links(doi_map_path, paper_links_dir):
    df = pd.read_csv(doi_map_path)

    renamed = 0
    skipped = 0
    missing = 0

    for _, row in df.iterrows():
        old_doi = row["Old_DOI"]
        new_doi = row["New_DOI"]

        old_path = os.path.join(paper_links_dir, old_doi)
        new_path = os.path.join(paper_links_dir, new_doi)

        if not os.path.exists(old_path):
            print(f"  MISSING: {old_doi}")
            missing += 1
            continue

        if os.path.exists(new_path):
            print(f"  SKIPPED (already exists): {new_doi}")
            skipped += 1
            continue

        # Ensure the target directory exists (e.g. 10.1109/)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        renamed += 1

    print(f"\nRenamed: {renamed}")
    print(f"Skipped (already exists): {skipped}")
    print(f"Missing source files: {missing}")


if __name__ == "__main__":
    rename_paper_links(DOI_MAP_FILENAME, PAPER_LINKS_DIR)
