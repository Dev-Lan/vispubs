"""Generate Parquet files from papers.csv and authors.csv with optimized types."""

import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PAPERS_CSV = os.path.join(REPO_ROOT, "public", "data", "papers.csv")
PAPERS_PARQUET = os.path.join(REPO_ROOT, "public", "data", "papers.parquet")
AUTHORS_CSV = os.path.join(REPO_ROOT, "public", "data", "authors.csv")
AUTHORS_PARQUET = os.path.join(REPO_ROOT, "public", "data", "authors.parquet")

AWARD_CATEGORIES = ["BA", "BCS", "BP", "HM", "TT"]
RESOURCE_CATEGORIES = ["C", "D", "O", "P", "PW", "V"]


def split_semicolon_list(value):
    """Split a semicolon-separated string into a list, or return empty list."""
    if pd.isna(value) or value == "":
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def convert_papers(csv_path, parquet_path):
    df = pd.read_csv(csv_path, dtype=str)

    # Year -> int
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    # Accessible, Early -> boolean
    for col in ["Accessible", "Early"]:
        df[col] = df[col].str.strip().str.lower() == "true"

    # Conference -> categorical
    df["Conference"] = df["Conference"].astype("category")

    # Semicolon-separated list columns
    df["AuthorNames-Deduped"] = df["AuthorNames-Deduped"].apply(split_semicolon_list)
    df["Award"] = df["Award"].apply(split_semicolon_list)
    df["Resources"] = df["Resources"].apply(split_semicolon_list)

    # Build pyarrow schema for list columns
    authors_array = pa.array(df["AuthorNames-Deduped"].tolist(), type=pa.list_(pa.string()))
    award_array = pa.array(
        df["Award"].tolist(), type=pa.list_(pa.dictionary(pa.int8(), pa.string()))
    )
    resources_array = pa.array(
        df["Resources"].tolist(), type=pa.list_(pa.dictionary(pa.int8(), pa.string()))
    )

    # Convert base DataFrame to arrow table, then replace list columns
    table = pa.Table.from_pandas(df.drop(columns=["AuthorNames-Deduped", "Award", "Resources"]))
    table = table.append_column("AuthorNames-Deduped", authors_array)
    table = table.append_column("Award", award_array)
    table = table.append_column("Resources", resources_array)

    pq.write_table(table, parquet_path)
    print(f"Wrote {len(df)} papers to {os.path.abspath(parquet_path)}")


def convert_authors(csv_path, parquet_path):
    df = pd.read_csv(csv_path, dtype=str)
    df.to_parquet(parquet_path, index=False)
    print(f"Wrote {len(df)} authors to {os.path.abspath(parquet_path)}")


def generate_parquet():
    convert_papers(PAPERS_CSV, PAPERS_PARQUET)
    convert_authors(AUTHORS_CSV, AUTHORS_PARQUET)


if __name__ == "__main__":
    generate_parquet()
