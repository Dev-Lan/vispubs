from os import close
from lxml import etree
import pandas as pd
import re

def parse_large_xml_with_dtd(xml_file, output_filename):

    columns = ['Conference', 'Year', 'Title', 'DOI', 'Abstract', 'AuthorNames-Deduped', 'Award', 'Resources']
    df = pd.DataFrame(columns=columns)

    # Define a context for iteratively parsing the XML file
    context = etree.iterparse(xml_file, events=('end',), load_dtd=True, huge_tree=True)

    venue_types = set(['article', 'inproceedings'])

    included_venues = set(['CHI', 'Vis', 'EuroVis'])

    count = 0

    for event, elem in context:

        if elem.tag not in venue_types:
            continue

        venue = get_venue(elem)
        if venue not in included_venues:
            continue

        title = get_text(elem, 'title')
        if title == '':
            # print('No title found:', elem) # TODO: check these elements
            continue
        if title[-1] == '.':
            title = title[:-1]

        year = get_text(elem, 'year')
        if venue == 'Vis':
            year = str(int(year) - 1)

        if is_front_matter(elem):
            continue

        authors = ';'.join(get_text_list(elem, 'author'))
        doi = get_doi(elem)

        # print(venue, year, title, doi, abstract, authors, award, resources)
        new_df = pd.DataFrame([{
            'Conference': venue,
            'Year': year,
            'Title': title,
            'DOI': doi,
            'Abstract': '',
            'AuthorNames-Deduped': authors,
            'Award': '',
            'Resources': ''
        }], columns=columns)
        df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv(output_filename, index=False)
    return

def get_text(elem, tag_name):
    sub_elem = elem.find(tag_name)
    if sub_elem is None:
        return None
    text = sub_elem.text if sub_elem.text is not None else ''
    return text.strip()

def get_text_list(elem, tag_name):
    sub_elems = elem.findall(tag_name)
    sub_elems = [x.text.strip() for x in sub_elems]
    return sub_elems

def get_venue(elem):
    booktitle = get_text(elem, 'booktitle')
    if booktitle is not None and booktitle == 'CHI':
        return 'CHI'

    journal = get_text(elem, 'journal')
    year = int(get_text(elem, 'year'))
    number = get_text(elem, 'number')
    if journal == 'IEEE Trans. Vis. Comput. Graph.':
        if year == 2021 and number == '2':
            return 'Vis'
        if year > 2016 and year != 2021 and number == '1':
            return 'Vis'
        else:
            return 'TVCG'
    if journal == 'Comput. Graph. Forum':
        if year > 2007 and number == '3':
            return 'EuroVis'
        else:
          return 'CGF'
    return 'UNKNOWN'

def get_doi(elem):
    ee = get_text_list(elem, 'ee')
    doi_org = 'https://doi.org/'
    for link in ee:
        if link.startswith('https://doi.org/'):
            return link.replace(doi_org, '', 1)
    return None

def is_front_matter(elem):
    title = get_text(elem, 'title').lower()
    if title in {'editorial.', 'guest editorial.', 'front matter.', 'editorials.', 'guest editorials.'}:
        return True
    pages = get_text(elem, 'pages')
    if pages is None:
        return False
    # 628:1-628:14 is valid
    # 1-13 is valid
    # 1 is invalid
    # i-xiii is invalid

    pages = re.split(r'[:\-]', pages) # split on ':' or '-'
    # if (len(pages) > 2):
    #   print(pages)
    if len(pages) <= 1:
        return True # Real papers will never be one page.

    # If they aren't all numbers, then it's something like 'xvii-xxiv'
    are_nums = [x.isdigit() for x in pages]
    return not all(are_nums)

parse_large_xml_with_dtd('./temp/dblp_filtered.xml', './temp/potential_new_papers.csv')
