import pandas as pd
import json

"""
Ingesting VIS data is different because it is helpful to load it into Vispubs before the data is officially published on tvcg.


To add the data there are three relevant files in ./input/vis24/

  A. vis_papers_rows for open practive.csv -  contains links to preprrints / preregistrations / acccessible flag
  B. ieeexport.csv - early access export from ieeeexplore. most important for the DOI and abstract
  C. papers.json - useful for the full author names
"""


def generate_vis25_data():
    # Load the data from the three files
    vis_papers = "./input/vis25/vis_papers_rows for open practive.csv"
    openpractices_path = "./input/vis25/full_vis25a_camera_20250814.csv"
    # ieeexport_path = "./input/vis24/ieeexport.csv"
    # papers_json_path = "./input/vis24/papers_ff.json"

    # Function to extract names and join them with semicolons
    def extract_names(cell):
        # convert json string to python object
        cell = json.loads(cell)
        # Extract names
        names = [record["name"] for record in cell]
        # Join names with semicolons
        return ";".join(names)

    df = pd.read_csv(vis_papers)
    # filter to event_prefix == 'v-full'
    df = df[df["event_prefix"] == "v-full"]
    df["AuthorNames-Deduped"] = df["authors"].apply(extract_names)

    # update id to get url https://ieeevis.org/year/2025/program/paper_{EXISTING_ID}.html
    df["VIS_URL"] = "https://ieeevis.org/year/2025/program/paper_" + df["id"] + ".html"

    df2 = pd.read_csv(openpractices_path)
    # convert Paper ID to string
    df2["Paper ID"] = df2["Paper ID"].astype(str)

    # merge df and df2 on 'title' and 'Title', only include rows that exist in df
    df = pd.merge(df, df2, left_on="program_paper_id", right_on="Paper ID", how="inner")

    df["DOI"] = "EARLY_ACCESS/" + df["id"]

    # TODO: preprint_link, accessible_pdf, award,

    # onnly keep relevant columns
    df = df[
        [
            "DOI",
            "Live Website",
            "Pre-registration",
            "Supplemental Material Link",
            "preprint_link",
            "VIS_URL",
            "title",
            "abstract",
            "AuthorNames-Deduped",
            # "award", # not recorded here.
            "accessible_pdf",
        ]
    ]

    # group / count by has_ff
    # ff_count = df["has_ff"].sum()
    # print(f"Number of papers with Fast Forward videos: {ff_count} out of {df.shape[0]}")
    # # zero
    # exit()

    # save as csv
    df["Conference"] = "Vis"
    df["Year"] = 2025
    # rename title to Title
    df = df.rename(columns={"title": "Title"})

    # rename abstract to Abstract
    df = df.rename(columns={"abstract": "Abstract"})

    # rename accessible_pdf to Accessible
    df = df.rename(columns={"accessible_pdf": "Accessible"})
    # convert the values "Accessible" → True, "" → False
    df["Accessible"] = df["Accessible"].apply(
        lambda x: True if x == "Accessible" else ""
    )

    df["Early"] = True

    # save to csv
    df.to_csv("./temp/vis25_with_resources.csv", index=False)
    # strip to columns we want in papers.csv:
    # DOI,Title,Abstract,AuthorNames-Deduped,Accessible,Conference,Year,Early
    df_papers = df[
        [
            "DOI",
            "Title",
            "Abstract",
            "AuthorNames-Deduped",
            "Accessible",
            "Conference",
            "Year",
            "Early",
        ]
    ]
    df_papers.to_csv("./temp/vis25.csv", index=False)


def expand_vis25_resources(filename="./vis25_with_resources/vis25.csv"):
    df = pd.read_csv(filename)

    # Create a list to hold the expanded rows
    expanded_rows = []

    # Iterate over each row in the resource_df
    for _, row in df.iterrows():
        # Append the preprint link
        if pd.notna(row["preprint_link"]):
            expanded_rows.append(
                {
                    "DOI": row["DOI"],
                    "icon": "paper",
                    "name": "Paper Preprint",
                    "url": row["preprint_link"],
                }
            )
        # Append the supplemental material link
        if pd.notna(row["Supplemental Material Link"]):
            expanded_rows.append(
                {
                    "DOI": row["DOI"],
                    "icon": "other",
                    "name": "Supplemental Material",
                    "url": row["Supplemental Material Link"],
                }
            )
        # Append the pre-registration link(s)
        if pd.notna(row["Pre-registration"]):
            prereg_list = row["Pre-registration"].split(";")
            for prereg in prereg_list:
                if "|" in prereg:
                    label, url = prereg.split("|")
                else:
                    label = "Preregistration"
                    url = prereg
                expanded_rows.append(
                    {"DOI": row["DOI"], "icon": "other", "name": label, "url": url}
                )
        # append the live website link(s)
        if pd.notna(row["Live Website"]):
            live_list = row["Live Website"].split(";")
            for live in live_list:
                if "|" in live:
                    label, url = live.split("|")
                else:
                    label = "Live Website"
                    url = live
                expanded_rows.append(
                    {"DOI": row["DOI"], "icon": "other", "name": label, "url": url}
                )
        # Append the VIS URL
        if pd.notna(row["VIS_URL"]):
            expanded_rows.append(
                {
                    "DOI": row["DOI"],
                    "icon": "other",
                    "name": "IEEE VIS Conference Page",
                    "url": row["VIS_URL"],
                }
            )

    # Convert the list of expanded rows into a DataFrame
    expanded_df = pd.DataFrame(expanded_rows)

    # Print the first few rows of the expanded DataFrame
    pd.set_option("display.max_columns", None)
    print(expanded_df)
    # save the expanded_df to a csv file
    expanded_df.to_csv("./temp/vis25_resources.csv", index=False)


if __name__ == "__main__":
    generate_vis25_data()
    # expand_vis25_resources()
    # expand_vis25_resources("./temp/vis25_manually_corrected.csv")
