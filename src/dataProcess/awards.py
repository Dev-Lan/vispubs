import logging
import pandas as pd

"""
Based on the awards listed in the reference award file.
The award file will have the following columns: Title,Award
update the Award column in paper file.
The paper will also have Title,Award columns. The
row should be matched based on title.
If there are any rows in the award file that are not in the paper file, a warning should be printed.
"""

AWARD_FILENAME = "./input/awards.csv"
# PAPERS_FILENAME = "../../public/data/papers.csv"
# OUTPUT_FILENAME = "../../public/data/papers.csv"
PAPERS_FILENAME = "./intermediate/VIS.csv"
OUTPUT_FILENAME = "./intermediate/VIS.csv"


def add_awards(award_filename, paper_filename, output_filename):
    logger = logging.getLogger("add_awards")
    # Read the award file and paper file into pandas DataFrames
    award_df = pd.read_csv(award_filename)
    paper_df = pd.read_csv(paper_filename)

    # Find all the rows that exist in award_df, but not in paper_df
    missing_rows = award_df[
        ~award_df.set_index(["Title"]).index.isin(paper_df.set_index(["Title"]).index)
    ]
    if not missing_rows.empty:
        logger.error("ERROR: Rows in the award file not found in the paper file.")
        logger.error(missing_rows)

    # Merge the award DataFrame with the paper DataFrame based and Title
    merged_df = pd.merge(paper_df, award_df, on=["Title"], how="left")

    # Update the Award column in the paper DataFrame with the values from the merged DataFrame
    paper_df["Award"] = merged_df["Award_y"]

    # Save the updated paper DataFrame to a new file
    paper_df.to_csv(output_filename, index=False)

    return


if __name__ == "__main__":
    add_awards(AWARD_FILENAME, PAPERS_FILENAME, OUTPUT_FILENAME)
