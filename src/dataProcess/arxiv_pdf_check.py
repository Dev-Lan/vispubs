import csv
import os
'''
Goes through every resource file, and checks for an arxiv link to the abstract. If found
it will replace it to the pdf link.

The abstract url is formatted as https://arxiv.org/abs/{arxiv_id}
The pdf url is formatted as https://arxiv.org/pdf/{arxiv_id}.pdf
'''

INPUT_PAPER_LIST_FILENAME = '../../public/data/papers.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'

def replace_arxiv_links():
    # Read the input paper list file
    with open(INPUT_PAPER_LIST_FILENAME, 'r') as file:
        reader = csv.reader(file)
        papers = list(reader)

    # Iterate through each resource file
    for row in papers:
        doi = row[3]

        abstract_url = f"arxiv.org/abs/"
        pdf_url = f"arxiv.org/pdf/"

        # Check if the resource file exists
        resource_file = os.path.join(ROOT_FOLDER, doi)
        if os.path.exists(resource_file):
            # Read the content of the resource file
            with open(resource_file, 'r') as file:
                content = file.read()

            # Replace the abstract URL with the PDF URL
            updated_content = content.replace(abstract_url, pdf_url)

            # Write the updated content back to the resource file
            with open(resource_file, 'w') as file:
                file.write(updated_content)

replace_arxiv_links()


