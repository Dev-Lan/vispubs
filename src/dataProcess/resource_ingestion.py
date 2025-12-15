import pandas as pd

"""
Given an input csv file, this will update the resource files.

The CSV file ahould have the following columns:
- DOI: the DOI of the paper
- name: the name of the resource
- url: the URL of the resource
- icon: the icon of the resource

For each row, the DOI will be used to find the corresponding paper in the intermediate file.
The resource will be added to the paper's resource list as long as the url is not already in the list.
"""


INPUT_FILENAME = "./temp/google_form_resources.csv"
ROOT_FOLDER = "../../public/data/paperLinks/"


def update_resources(input_filename):
    #  load into pandas df
    new_resources = pd.read_csv(input_filename)
    #  iterate through the rows
    for index, row in new_resources.iterrows():
        doi = row["DOI"]
        name = row["name"]
        url = row["url"]
        icon = row["icon"]
        #  add the row to the resource files
        add_row_to_resource_files(doi, name, url, icon)
    return


def add_row_to_resource_files(doi, name, url, icon):
    with open(ROOT_FOLDER + doi, "a+") as file:
        #  Check if the url is already in the file
        file.seek(0)  # Reset file pointer to the beginning
        for line in file.readlines():
            if url in line:
                return
        # seek to the end of the file
        file.seek(0, 2)
        file.write(f"\n{name},{url},{icon}")
    return


if __name__ == "__main__":
    update_resources(INPUT_FILENAME)
