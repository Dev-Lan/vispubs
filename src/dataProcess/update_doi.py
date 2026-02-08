"""
update_doi.py

Update early access papers on vispubs once there are actual DOIs available.
All placeholder/fake DOIs are assumed to begin with "EARLY_ACCESS"

Given a csv with columns "Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award"
that include real DOI values, update a different table with the same columns,
replacing any placeholder DOIs with the real ones.

Papers will be matched based on the title field.
A map from old DOI to new DOI will be created and saved to ./temp/doi_updates.csv

As a final check the number of papers with placeholder DOIs before and after
the update will be printed.

Usage:
  python update_doi.py --real real_with_doi.csv --target target_table.csv --out updated_target.csv
"""

import pandas as pd
import os

WITH_DOI_FILENAME = "./temp/vis25_from_ieee_jan.csv"
TARGET_FILENAME = "./intermediate/VIS.csv"


def update_early_access_dois(source_path, target_path):
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
    doi_map = source_df.drop_duplicates("NormalizedTitle").set_index("NormalizedTitle")[
        "DOI"
    ]

    # 3. Apply updates to target
    # We track updates to create the log later
    update_log_entries = []

    def apply_update(row):
        if str(row["DOI"]).startswith("EARLY_ACCESS"):
            norm_t = normalize_title(row["Title"])
            if norm_t in doi_map:
                new_doi = doi_map[norm_t]
                update_log_entries.append({"Old_DOI": row["DOI"], "New_DOI": new_doi})
                return new_doi
        return row["DOI"]

    target_df["DOI"] = target_df.apply(apply_update, axis=1)

    # 4. Save the update log to ./temp/doi_updates.csv
    if update_log_entries:
        os.makedirs("./temp", exist_ok=True)
        pd.DataFrame(update_log_entries).to_csv("./temp/doi_updates.csv", index=False)

    # 5. Final Count
    final_placeholder_count = (
        target_df["DOI"].str.startswith("EARLY_ACCESS", na=False).sum()
    )
    print(f"Placeholder DOIs after update: {final_placeholder_count}")
    print(
        f"Successfully updated {initial_placeholder_count - final_placeholder_count} records."
    )

    # Save the updated table
    target_df.to_csv(target_path, index=False)


if __name__ == "__main__":
    # Ensure these files exist in your directory
    update_early_access_dois(WITH_DOI_FILENAME, TARGET_FILENAME)


# import argparse
# import csv
# import os
# import sys
# from collections import defaultdict

#!/usr/bin/env python3

# PLACEHOLDER_PREFIX = "EARLY_ACCESS"
# MAPPING_DIR = "./temp"
# MAPPING_FILE = os.path.join(MAPPING_DIR, "doi_updates.csv")


# def normalize_title(t: str) -> str:
#     if t is None:
#         return ""
#     # Basic normalization: strip, collapse whitespace, lowercase
#     return " ".join(t.split()).lower()


# def load_real_dois(path):
#     """
#     Load CSV of real DOIs. Return dict: normalized_title -> list of rows (dicts).
#     """
#     by_title = defaultdict(list)
#     with open(path, newline="", encoding="utf-8") as fh:
#         reader = csv.DictReader(fh)
#         for row in reader:
#             title = normalize_title(row.get("Title", ""))
#             by_title[title].append(row)
#     return by_title


# def update_target(real_map, target_path, out_path):
#     """
#     Read target CSV, replace placeholder DOIs when a real DOI matches by title.
#     Returns stats and mapping rows for saved mapping file.
#     """
#     mapping_rows = []
#     updated_count = 0
#     placeholder_before = 0
#     placeholder_after = 0
#     unmatched_placeholders = 0

#     with open(target_path, newline="", encoding="utf-8") as inf:
#         reader = csv.DictReader(inf)
#         fieldnames = reader.fieldnames
#         if not fieldnames:
#             raise RuntimeError("Target CSV has no header/columns.")
#         rows = list(reader)

#     for row in rows:
#         doi = (row.get("DOI") or "").strip()
#         title_norm = normalize_title(row.get("Title", ""))
#         if doi.startswith(PLACEHOLDER_PREFIX):
#             placeholder_before += 1
#             candidates = real_map.get(title_norm, [])
#             # Find first candidate with a non-placeholder DOI
#             chosen = None
#             for cand in candidates:
#                 cand_doi = (cand.get("DOI") or "").strip()
#                 if cand_doi and not cand_doi.startswith(PLACEHOLDER_PREFIX):
#                     chosen = cand
#                     break
#             if chosen:
#                 old_doi = doi
#                 new_doi = (chosen.get("DOI") or "").strip()
#                 if new_doi and new_doi != old_doi:
#                     row["DOI"] = new_doi
#                     updated_count += 1
#                     mapping_rows.append(
#                         {
#                             "Conference": row.get("Conference", ""),
#                             "Year": row.get("Year", ""),
#                             "Title": row.get("Title", ""),
#                             "OldDOI": old_doi,
#                             "NewDOI": new_doi,
#                         }
#                     )
#             else:
#                 unmatched_placeholders += 1

#     # Count placeholders after update
#     for row in rows:
#         doi = (row.get("DOI") or "").strip()
#         if doi.startswith(PLACEHOLDER_PREFIX):
#             placeholder_after += 1

#     # Write updated target CSV
#     os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
#     with open(out_path, "w", newline="", encoding="utf-8") as outf:
#         writer = csv.DictWriter(outf, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in rows:
#             writer.writerow(row)

#     return {
#         "placeholder_before": placeholder_before,
#         "placeholder_after": placeholder_after,
#         "updated_count": updated_count,
#         "unmatched_placeholders": unmatched_placeholders,
#         "mapping_rows": mapping_rows,
#     }


# def save_mapping(mapping_rows):
#     os.makedirs(MAPPING_DIR, exist_ok=True)
#     fieldnames = ["Conference", "Year", "Title", "OldDOI", "NewDOI"]
#     with open(MAPPING_FILE, "w", newline="", encoding="utf-8") as mf:
#         writer = csv.DictWriter(mf, fieldnames=fieldnames)
#         writer.writeheader()
#         for r in mapping_rows:
#             writer.writerow(r)


# def main(argv):
#     parser = argparse.ArgumentParser(
#         description="Update EARLY_ACCESS DOIs in a target CSV using a real-DOI CSV."
#     )
#     parser.add_argument(
#         "--real",
#         required=True,
#         help="CSV file containing real DOIs (has Title and DOI columns).",
#     )
#     parser.add_argument(
#         "--target",
#         required=True,
#         help="Target CSV to update (will be read and updated).",
#     )
#     parser.add_argument(
#         "--out", required=True, help="Output path for the updated target CSV."
#     )
#     args = parser.parse_args(argv)

#     if not os.path.isfile(args.real):
#         print(f"Real DOI CSV not found: {args.real}", file=sys.stderr)
#         sys.exit(2)
#     if not os.path.isfile(args.target):
#         print(f"Target CSV not found: {args.target}", file=sys.stderr)
#         sys.exit(2)

#     real_map = load_real_dois(args.real)
#     stats = update_target(real_map, args.target, args.out)
#     save_mapping(stats["mapping_rows"])

#     print(f"Placeholder DOIs before: {stats['placeholder_before']}")
#     print(f"Placeholder DOIs after:  {stats['placeholder_after']}")
#     print(f"Updated DOIs:           {stats['updated_count']}")
#     if stats["unmatched_placeholders"] > 0:
#         print(
#             f"Unmatched placeholders (no real DOI found by title): {stats['unmatched_placeholders']}"
#         )
#     print(f"Mapping saved to: {MAPPING_FILE}")


# if __name__ == "__main__":
#     main(sys.argv[1:])
