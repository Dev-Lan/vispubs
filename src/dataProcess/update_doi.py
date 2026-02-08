"""
update_doi.py

Update early access papers on vispubs once there are actual DOIs available.
All placeholder/fake DOIs are assumed to begin with "EARLY_ACCESS"

Given a csv with columns "Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award"
that include real DOI values, update a different table with the same columns,
replacing any placeholder DOIs with the real ones. Abstracts are also updated
from the source file when the source abstract is non-empty.

Papers will be matched based on the title field.
A map from old DOI to new DOI will be appended to DOI_MAP_FILENAME (default:
./temp/doi_updates.csv). Duplicate entries already present in the file will
not be added again.

As a final check the number of papers with placeholder DOIs before and after
the update will be printed.

Usage:
  python update_doi.py
"""

import pandas as pd
import os

WITH_DOI_FILENAME = "./temp/vis25_from_ieee_jan.csv"
TARGET_FILENAME = "./intermediate/VIS.csv"
DOI_MAP_FILENAME = "./temp/doi_updates.csv"


def update_early_access_dois(source_path, target_path, doi_map_path=DOI_MAP_FILENAME):
    source_df = pd.read_csv(source_path)
    target_df = pd.read_csv(target_path)

    # Helper function to clean titles for matching
    def normalize_title(title):
        if pd.isna(title):
            return ""
        return " ".join(str(title).lower().split())

    # 1. Count placeholder DOIs before update
    initial_placeholder_count = (
        target_df["DOI"].str.startswith("EARLY_ACCESS", na=False).sum()
    )
    print(f"Placeholder DOIs before update: {initial_placeholder_count}")

    # 2. Create a normalized map from the source data
    # We add a temporary column 'NormalizedTitle' to source
    source_df["NormalizedTitle"] = source_df["Title"].apply(normalize_title)
    source_deduped = source_df.drop_duplicates("NormalizedTitle").set_index(
        "NormalizedTitle"
    )
    doi_map = source_deduped["DOI"]
    abstract_map = source_deduped["Abstract"]

    # 3. Apply DOI and abstract updates to target
    # We track DOI updates to create the log later
    update_log_entries = []
    abstract_update_count = 0

    for idx, row in target_df.iterrows():
        norm_t = normalize_title(row["Title"])

        # Update DOI if it's a placeholder
        if str(row["DOI"]).startswith("EARLY_ACCESS") and norm_t in doi_map:
            new_doi = doi_map[norm_t]
            update_log_entries.append({"Old_DOI": row["DOI"], "New_DOI": new_doi})
            target_df.at[idx, "DOI"] = new_doi

        # Update abstract if the source has a non-empty one
        if norm_t in abstract_map and not pd.isna(abstract_map[norm_t]) and str(abstract_map[norm_t]).strip():
            target_df.at[idx, "Abstract"] = abstract_map[norm_t]
            abstract_update_count += 1

    # 4. Append the update log to doi_map_path, skipping duplicates
    if update_log_entries:
        os.makedirs(os.path.dirname(doi_map_path), exist_ok=True)
        new_entries_df = pd.DataFrame(update_log_entries)

        if os.path.exists(doi_map_path):
            existing_df = pd.read_csv(doi_map_path)
            # Drop entries whose Old_DOI already appears in the existing file
            new_entries_df = new_entries_df[
                ~new_entries_df["Old_DOI"].isin(existing_df["Old_DOI"])
            ]
            if not new_entries_df.empty:
                new_entries_df.to_csv(
                    doi_map_path, mode="a", header=False, index=False
                )
        else:
            new_entries_df.to_csv(doi_map_path, index=False)

    # 5. Final Count
    final_placeholder_count = (
        target_df["DOI"].str.startswith("EARLY_ACCESS", na=False).sum()
    )
    print(f"Placeholder DOIs after update: {final_placeholder_count}")
    print(
        f"Successfully updated {initial_placeholder_count - final_placeholder_count} DOIs."
    )
    print(f"Successfully updated {abstract_update_count} abstracts.")

    # Save the updated table
    target_df.to_csv(target_path, index=False)


if __name__ == "__main__":
    # Ensure these files exist in your directory
    update_early_access_dois(WITH_DOI_FILENAME, TARGET_FILENAME)
