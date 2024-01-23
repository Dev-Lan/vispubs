import csv
import requests
import os
import urllib
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
NOT_FOUND_LIST_FILENAME = './openSourceNotFoundList.CSV'

def search_preprint_versions():
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
            year = row[1]
            title = row[2]
            doi = row[3]
            print(str(index) + ": " + conf + "-" + year + ", " + title[:45] + '...')

            index += 1
            already_added = preprint_already_added(doi)
            if already_added:
                print('\t✅ Skipping, already added')
                found_links += 1
                continue

            link = search_arxiv_api(title)
            if link is not None:
                print("\t🍺 Found arXiv")
                found_arxiv += 1
            else:
                link = search_osf_api(browser, title)
                if link is not None:
                    print("\t🍺 Found OSF")
                    found_osf += 1

            if link is not None:
                add_link_to_file(link, doi)
                found_links += 1
                added_links += 1
            else:
                print("\t❌ Not found")
                # add doi and title to end of OPEN_SOURCE_NOT_FOUND_LIST_FILENAME
                with open(NOT_FOUND_LIST_FILENAME, 'a') as not_found_file:
                    not_found_file.write(doi + ',' + title + '\n')

            wait_and_print(5)
    browser.quit()
    print('Finished searching for preprint versions.')
    print('Added', added_links, ', found', found_links, ', of', index, 'total papers.')
    print('Found', found_osf, 'on OSF and', found_arxiv, 'on arXiv.')

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
            # print(result)
            # print(result.get_attribute('innerHTML'))
            # print(result.get_attribute('href'))
            # print('='*20)
            if close_enough(result.text, title):
                return result.get_attribute('href')
        return None
    except Exception as error:
        # print the error
        print('🐛🐞 osf error 🐞🐛')
        print(error)
        return None

def close_enough(s1, s2):
    d = nltk.edit_distance(s1, s2)
    return d <= 3

def search_arxiv_api(title):
    try:
        # URL encode the title
        title_query = urllib.parse.quote(title)

        # Build the API request URL
        url = f'http://export.arxiv.org/api/query?search_query=ti:{title_query}'

        # Send the request and parse the response
        response = urllib.request.urlopen(url)
        feed = feedparser.parse(response)

        # Iterate over the entries
        for entry in feed.entries:
            candidate_title = entry.title.strip()
            if close_enough(candidate_title, title):
                return entry.link

        # If no close enough match is found, return None
        return None
    except Exception as error:
        # print the error
        print('🐛🐞 arxiv error 🐞🐛')
        print(error)
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
        if len(lines) == 1:
            lines[0] += '\n'
        lines.insert(1, 'Paper Preprint,' + link + ',paper\n')
        file.seek(0)
        file.writelines(lines)

search_preprint_versions()

