import os
import csv
import json
'''
This file will open a INPUT_METADATA_FILENAME json file and add rows
to the corresponding paper link files in the ROOT_FOLDER. It will
determine the file location based on the `doi` attribute. If this is
not present it will check the `external_paper_links` and use the text
after `doi.org/` as the doi. If this is not present it will use the
`title` attribute and see if that exists in the `INPUT_PAPER_LIST_FILENAME`,
and if so use the doi from that file. If none of these are present it
will skip the row.

For every paper that is found it will add rows to the existing resource files.
If any of these attributes are not present, do not add anything:

input attribute, output name, output icon
ff_link, Fast Forward, video
youtube_ff_id, Fast Forward, video
prerecorded_video_link, Prerecorded Talk, video
youtube_prerecorded_link, Prerecorded Talk, video
'''

INPUT_METADATA_FILENAME = './temp/paper_list_22.json'
INPUT_PAPER_LIST_FILENAME = '../../public/data/papers.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'

RESOURCE_ATTRIBUTES = {
    'ff_link': ('Fast Forward', 'video'),
    'youtube_ff_link': ('Fast Forward', 'video'),
    'prerecorded_video_link': ('Prerecorded Talk', 'video'),
    'youtube_prerecorded_link': ('Prerecorded Talk', 'video'),

}

def populate_vis_resources():

    with open(INPUT_METADATA_FILENAME, 'r') as metadata_file:
        metadata = json.load(metadata_file)

    title_doi_map = populate_title_doi_map(INPUT_PAPER_LIST_FILENAME)
    total_count = len(metadata)
    processed_count = 0
    for row_key in metadata:
        row = metadata[row_key]
        # print(row)
        doi = row.get('doi')
        if not doi:
            external_paper_links = row.get('external_paper_links')
            if external_paper_links:
                doi = external_paper_links.split('doi.org/')[1] if 'doi.org/' in external_paper_links else None
            if not doi:
                title = row.get('title')
                if title:
                    doi = title_doi_map.get(title, None)
        if doi:
            if not os.path.exists(ROOT_FOLDER + doi):
                continue
            # Add rows to the existing resource files
            add_rows_to_resource_files(doi, row)
            processed_count += 1
    print(f'Processed {processed_count} out of {total_count} papers.')

def populate_title_doi_map(input_paper_list_filename):
    title_doi_map = {}
    # Implement the logic to populate the title_doi_map
    with open(input_paper_list_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            title = row[2]
            doi = row[3]
            title_doi_map[title] = doi
    return title_doi_map

def add_rows_to_resource_files(doi, row):
    with open(ROOT_FOLDER + doi, 'a+') as file:
        for attribute, (name, icon) in RESOURCE_ATTRIBUTES.items():
            value = row.get(attribute)
            if value:
                file.write(f'\n{name},{value},{icon}')

populate_vis_resources()