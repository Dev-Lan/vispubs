import logging
import csv
import json
from pyparsing import C
import os
import urllib
import urllib.request
import feedparser
import time
import sys
import nltk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
'''
This scripts searches for preprint versions of papers using arxiv
and osf api. It will check every row in the INPUT_METADATA_FILENAME.
It will first search the osf api, if it isn't found it will search
the arxiv api. If it is found it will add the link to the corresponding
paper link file in the ROOT_FOLDER. It will determine the file location
based on the `doi` attribute.
'''

INPUT_PAPER_LIST_FILENAME = '../../public/data/papers.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'
NOT_FOUND_LIST_FILENAME = './intermediate/openSourceNotFoundList.csv'
CHECK_OSF = False

def search_preprint_versions(year=None, conference=None, dois=None, recheck=False):
    '''Search for preprints, optionally restricted to a subset of papers.

    With no arguments every paper is considered, which is how main.py calls it.
    The filters exist because a paper added outside the main pipeline (see
    ingest_eurovis_26.py) would otherwise need a full pass over the corpus --
    thousands of papers at 5 seconds each -- to be reached.

    recheck ignores the previously-searched-and-not-found list, for re-running
    after the search itself has been improved.
    '''
    logger = logging.getLogger('search_preprint_versions')
    wanted_dois = {d.strip().lower() for d in dois} if dois else None
    if CHECK_OSF:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        # executable_path param is not needed if you updated PATH
        browser = webdriver.Chrome(options=options)#, executable_path='YOUR_PATH/chromedriver.exe')

    with open(INPUT_PAPER_LIST_FILENAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        index = 0
        found_links = 0
        added_links = 0
        found_arxiv = 0
        found_osf = 0
        for row in reader:
            conf = row[0]
            year_value = row[1]
            title = row[2]
            doi = row[3]

            if year is not None and year_value != str(year):
                continue
            if conference is not None and conf != conference:
                continue
            if wanted_dois is not None and doi.strip().lower() not in wanted_dois:
                continue

            print_message = str(index) + ": " + conf + "-" + year_value + ", " + title[:45] + '...'
            index += 1
            already_added = preprint_already_added(doi)
            if already_added:
                logger.debug(print_message)
                logger.debug('\t✅ Skipping, already added')
                found_links += 1
                continue

            if not recheck and preprint_already_searched_and_not_found(doi):
                logger.debug(print_message)
                logger.debug('\t🤷 Skipping, searched in past and not found')
                continue

            logger.info(print_message)
            link = search_arxiv_api(title)
            if link is not None:
                logger.info("\t🍺 Found arXiv")
                found_arxiv += 1
            else:
                # The title search misses retitled preprints, and sometimes does
                # not surface a paper whose title matches exactly. Semantic
                # Scholar maps the DOI straight to an arXiv id instead.
                link = search_semantic_scholar_arxiv(doi)
                if link is not None:
                    logger.info("\t🍺 Found arXiv (via Semantic Scholar DOI lookup)")
                    found_arxiv += 1
            if link is None and CHECK_OSF:
                link = search_osf_api(browser, title)
                if link is not None:
                    logger.info("\t🍺 Found OSF")
                    found_osf += 1

            if link is not None:
                add_link_to_file(link, doi)
                found_links += 1
                added_links += 1
            else:
                logger.info("\t❌ Not found")
                # add doi and title to end of OPEN_SOURCE_NOT_FOUND_LIST_FILENAME,
                # unless a recheck already recorded it on an earlier pass
                if not preprint_already_searched_and_not_found(doi):
                    with open(NOT_FOUND_LIST_FILENAME, 'a') as not_found_file:
                        not_found_file.write(doi + ',' + title + '\n')

            wait_and_print(5)
    if CHECK_OSF:
        browser.quit()
    logger.info('Finished searching for preprint versions.')
    logger.info(f"Added {added_links}, found {found_links}, of {index} total papers.")
    logger.info(f"Found {found_osf} on OSF and {found_arxiv} on arXiv.")

def wait_and_print(seconds):
    for i in range(seconds, 0, -1):
        sys.stdout.write('\r')
        sys.stdout.write('\tWaiting {} seconds...'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\r')
    sys.stdout.write(' '*30)
    sys.stdout.write('\r')
    return

def search_osf_api(browser, title):
    logger = logging.getLogger('search_preprint_versions')
    try:
        # Navigate to the OSF preprints search page
        browser.get('https://osf.io/search?resourceType=Preprint')

        # Find the search box element
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )

        # Type the title into the search box and press Enter
        search_box.send_keys(title + Keys.RETURN)

        # Wait 10 seconds, for results to hopefully load
        wait_and_print(10)
        # .until(
            # EC.presence_of_element_located((By.TAG, "search-result"))
        # )

        # Extract the titles and links of the search results
        results = browser.find_elements(By.TAG_NAME, 'a')
        for result in results:
            if close_enough(result.text, title):
                return result.get_attribute('href')
        return None
    except Exception as error:
        # print the error
        logger.error('🐛🐞 osf error 🐞🐛')
        logger.error(error)
        return None

def close_enough(s1, s2):
    d = nltk.edit_distance(s1.lower(), s2.lower())
    return d <= 3

def search_semantic_scholar_arxiv(doi):
    '''Look up a paper's arXiv preprint by DOI via Semantic Scholar.

    The arXiv title search misses preprints whose title was reworded before
    publication, and it also fails on titles it simply does not surface in its
    own results. Semantic Scholar records the DOI-to-arXiv relationship
    directly, so no title comparison is involved and no false match is possible.
    '''
    logger = logging.getLogger('search_preprint_versions')
    if not doi:
        return None
    url = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=externalIds'
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
        arxiv_id = (data.get('externalIds') or {}).get('ArXiv')
        if arxiv_id:
            return f'https://arxiv.org/pdf/{arxiv_id}'
        return None
    except Exception as error:
        logger.error('🐛🐞 semantic scholar error 🐞🐛')
        logger.error(error)
        return None


def search_arxiv_api(title):
    logger = logging.getLogger('search_preprint_versions')
    try:
        # URL encode the title
        title_query = title.replace(':', '\:') # arxiv api doesn't like colons
        title_query = urllib.parse.quote(title_query)

        # Build the API request URL
        url = f'http://export.arxiv.org/api/query?search_query=ti:{title_query}'

        # Send the request and parse the response
        response = urllib.request.urlopen(url)
        feed = feedparser.parse(response)

        # Iterate over the entries
        for entry in feed.entries:
            candidate_title = entry.title.strip()
            if close_enough(candidate_title, title):
                link = entry.link
                return link.replace(f"arxiv.org/abs/", f"arxiv.org/pdf/")

        # If no close enough match is found, return None
        return None
    except Exception as error:
        # print the error
        logger.error('🐛🐞 arxiv error 🐞🐛')
        logger.error(error)
        return None


# Performance note for this function and the next one:
# It would be faster to cache the file names in a set and
# reuse that set for each paper, but I'm also waiting 5-15
# seconds between each search, so it's not a big deal.
# also probably will only run this script once or twice.
def preprint_already_added(doi):
    filename = os.path.join(ROOT_FOLDER, doi)
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'Paper Preprint' in line:
                return True
        return False

def preprint_already_searched_and_not_found(doi):
    with open(NOT_FOUND_LIST_FILENAME, 'r') as not_found_file:
        lines = not_found_file.readlines()
        for line in lines:
            if doi == line.split(',')[0]:
                return True
        return False

def add_link_to_file(link, doi):
    filename = os.path.join(ROOT_FOLDER, doi)
    with open(filename, 'r+') as file:
        # insert into the second line
        lines = file.readlines()
        if len(lines) == 1:
            lines[0] += '\n'
        lines.insert(1, 'Paper Preprint,' + link + ',paper\n')
        file.seek(0)
        file.writelines(lines)


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Search for preprint versions of papers')
  parser.add_argument('--year', help='only search papers from this year')
  parser.add_argument('--conference', help='only search papers from this venue, e.g. EuroVis')
  parser.add_argument('--doi', nargs='+', metavar='DOI', help='only search these DOIs')
  parser.add_argument('--recheck', action='store_true',
                      help='ignore the previously-not-found list and search again')
  args = parser.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(message)s')
  search_preprint_versions(year=args.year, conference=args.conference,
                           dois=args.doi, recheck=args.recheck)

