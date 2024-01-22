import csv
import requests
import os
import urllib
import feedparser
import time
import sys
import nltk
'''
This scripts searches for preprint versions of papers using arxiv
and osf api. It will check every row in the INPUT_METADATA_FILENAME.
It will first search the osf api, if it isn't found it will search
the arxiv api. If it is found it will add the link to the corresponding
paper link file in the ROOT_FOLDER. It will determine the file location
based on the `doi` attribute.
'''

INPUT_PAPER_LIST_FILENAME = '../../public/data/papers_test.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'

def search_preprint_versions():
    with open(INPUT_PAPER_LIST_FILENAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        index = 0
        found_links = 0
        added_links = 0
        for row in reader:
            conf = row[0]
            year = row[1]
            title = row[2]
            doi = row[3]
            print(str(index) + ": " + conf + "-" + year + ", " + title[:45] + '...')

            index += 1
            already_added = preprint_already_added(doi)
            if already_added:
                found_links += 1
                continue

            link = search_osf_api(title)
            if link is None:
                link = search_arxiv_api(title)
            if link is None:
                link = search_bioarxiv_api(title)
            if link:
                print("\tFound")
                add_link_to_file(link, doi)
                found_links += 1
                added_links += 1

            wait_time = 5
            for i in range(wait_time, 0, -1):
                sys.stdout.write('\r')
                sys.stdout.write('Waiting {} seconds...'.format(i))
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write('\r')
            sys.stdout.write(' '*30)
            sys.stdout.write('\r')
    print('Finished searching for preprint versions.')
    print('Added', added_links, ', found', found_links, ', of', index, 'total papers.')

def search_osf_api(title):
    # TODO
        return None


def close_enough(s1, s2):
    d = nltk.edit_distance(s1, s2)
    return d <= 3

def search_arxiv_api(title):
    # URL encode the title
    title_query = urllib.parse.quote(title)

    # Build the API request URL
    url = f'http://export.arxiv.org/api/query?search_query=ti:{title_query}'

    # Send the request and parse the response
    response = urllib.request.urlopen(url)
    feed = feedparser.parse(response)

    # Iterate over the entries
    for entry in feed.entries:
        # If the entry's title is exactly the same as the title we're searching for, return its link
        candidate_title = entry.title.strip()
        # print(candidate_title)
        # print(title)
        # dist = nltk.edit_distance(candidate_title, title)
        # print(dist)
        # print('---')
        if close_enough(candidate_title, title):
            return entry.link

    # If no exact match is found, return None
    return None

def search_bioarxiv_api(title):
    # TODO
    return None

def preprint_already_added(doi):
    filename = os.path.join(ROOT_FOLDER, doi)
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'Paper Preprint' in line:
                return True
        return False

def add_link_to_file(link, doi):
    filename = os.path.join(ROOT_FOLDER, doi)
    with open(filename, 'r+') as file:
        # insert into the second line
        lines = file.readlines()
        lines.insert(1, 'Paper Preprint,' + link + ',paper\n')
        file.seek(0)
        file.writelines(lines)

search_preprint_versions()

