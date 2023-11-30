from unittest import skip
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString

# Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award

# source page with links to all years of EuroVis
# https://dblp.org/db/conf/vissym/index.html
def main():
    csv_string = 'Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award\n'

    flat_list_urls = {'https://dblp.org/db/journals/cgf/cgf41.html#nr3'}
    url_list = [
        # 'https://dblp.org/db/journals/cgf/cgf41.html#nr3', # 2022
        # 'https://dblp.org/db/journals/cgf/cgf40.html#nr3', # 2021
        # 'https://dblp.org/db/journals/cgf/cgf39.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf38.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf37.html#nr3', # 2018
        # 'https://dblp.org/db/journals/cgf/cgf36.html#nr3', 
        # 'https://dblp.org/db/journals/cgf/cgf35.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf34.html#nr3', # 2015
        # 'https://dblp.org/db/journals/cgf/cgf33.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf32.html#nr3', # 2013
        # 'https://dblp.org/db/journals/cgf/cgf31.html#nr3pt1',
        # 'https://dblp.org/db/journals/cgf/cgf30.html#nr3', # 2011 (keynote/capstone)
        # 'https://dblp.org/db/journals/cgf/cgf29.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf28.html#nr3',
        # 'https://dblp.org/db/journals/cgf/cgf27.html#nr3', # 2008
        'https://dblp.org/db/conf/vissym/eurovis2007.html', # 2007
        'https://dblp.org/db/conf/vissym/eurovis2006.html',
        'https://dblp.org/db/conf/vissym/eurovis2005.html',
        'https://dblp.org/db/conf/vissym/vissym2004.html', # nested, skip invited
        'https://dblp.org/db/conf/vissym/vissym2003.html', # also nested
        'https://dblp.org/db/conf/vissym/vissym2002.html',
        'https://dblp.org/db/conf/vissym/vissym2001.html',
        'https://dblp.org/db/conf/vissym/vissym2000.html',
        'https://dblp.org/db/conf/vissym/vissym1999.html'
    ]
    pre2008 = True
    #get 1999 to 2007
    # pre 2007, this may be enough document.getElementsByClassName('publ-list')
    # https://api.crossref.org/${DOI}/transform/application/vnd.crossref.unixsd+xml

    # 2022 single list format
    # fp = urllib.request.urlopen("https://dblp.org/db/journals/cgf/cgf41.html#nr3")

    # 2021 - 2008 multi-list, some with skippable sections
    i = 1
    for url in url_list:
        print('Processing (', i, ' of ', len(url_list), '): ', url)
        i += 1
        fp = urllib.request.urlopen(url)
        nested = url not in flat_list_urls
        mybytes = fp.read()

        page_html = mybytes.decode("utf8")
        fp.close()

        page_html = page_html.replace('<br />', '') # causes issues with soup's parsing.
        # <br />

        soup = BeautifulSoup(page_html, 'html.parser')
        if not pre2008:
            key = url.split('#')[-1]
            header = soup.select('#' + key)[0]

        skip_sections = {'front matter', 'keynote', 'capstone'}
        if pre2008:
            # document.getElementsByClassName('publ-list')
            publication_list_of_lists = soup.select('.publ-list')
            first = True
            for publication_list in publication_list_of_lists:
                # beautifulsoup, get number of children inside publication_list
                length = len(publication_list.contents)      
                if (length == 1):
                    first = False
                    # hacky way to skip the intro/invited talk of 2003/2004
                    continue
                for pub in publication_list.children:
                    if first:
                        first = False
                        continue
                    pub_info = parse_pub(pub)
                    csv_string += pub_info + '\n'
        elif nested:
            # curr = header.parent
            skip_next = False
            # while curr.next_sibling:
            for curr in header.parent.next_siblings:
                # print(curr)
                # curr = curr.next_sibling
                # print(curr)
                if curr.text.strip().lower() in skip_sections:
                    skip_next = True
                    continue
                if skip_next:
                    skip_next = False
                    continue
                if type(curr) == NavigableString:
                    continue
                if len(curr.select('#nr4')) > 0:
                    break
                if 'publ-list' not in curr['class']:
                    continue
                for pub in curr.children:
                    pub_info = parse_pub(pub)
                    csv_string += pub_info + '\n'
        else:
            publication_list = header.parent.next_sibling.next_sibling
            # publication_list = soup.select('#main > ul:nth-child(96)')[0]
            for pub in publication_list.children:
                csv_string += parse_pub(pub) + '\n'

    # print(csv_string)
    with open('eurovis-pre-2008.csv', 'w') as f:
        f.write(csv_string)
    return


def parse_pub(pub):
        title = pub.find(class_="title").text.removesuffix('.')
        title = '"' + title + '"'
        year = pub.find(itemprop="datePublished")['content']
        doi = pub.find(class_='publ').find('a')['href'].removeprefix('https://doi.org/')
        authors = pub.find_all(itemprop="author")
        author_names = [author.find(itemprop="name")['title'] for author in authors]
        authors_string = ";".join(author_names)
        conference = 'EuroVis'
        abstract = ''
        award = ''
        return ','.join([conference, year, title, doi, abstract, authors_string, award])


if __name__ == '__main__':
    main()