import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString

# Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award

# source page with links to all years of CHI
# https://dblp.org/db/conf/chi/index.html
def main():
    csv_string = 'Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award\n'

    url_list = [
        'https://dblp.org/db/conf/chi/chi2023.html',
        'https://dblp.org/db/conf/chi/chi2022.html',
        'https://dblp.org/db/conf/chi/chi2021.html',
        'https://dblp.org/db/conf/chi/chi2020.html',
        'https://dblp.org/db/conf/chi/chi2019.html',
        'https://dblp.org/db/conf/chi/chi2018.html',
        'https://dblp.org/db/conf/chi/chi2017.html',
        'https://dblp.org/db/conf/chi/chi2016.html',
        'https://dblp.org/db/conf/chi/chi2015.html',
        'https://dblp.org/db/conf/chi/chi2014.html',
        'https://dblp.org/db/conf/chi/chi2013.html',
        'https://dblp.org/db/conf/chi/chi2012.html',
        'https://dblp.org/db/conf/chi/chi2011.html',
        'https://dblp.org/db/conf/chi/chi2010.html',
        'https://dblp.org/db/conf/chi/chi2009.html',
        'https://dblp.org/db/conf/chi/chi2008.html',
        'https://dblp.org/db/conf/chi/chi2007.html',
        'https://dblp.org/db/conf/chi/chi2006.html',
        'https://dblp.org/db/conf/chi/chi2005.html',
        'https://dblp.org/db/conf/chi/chi2004.html',
        'https://dblp.org/db/conf/chi/chi2003.html',
        'https://dblp.org/db/conf/chi/chi2002.html',
        'https://dblp.org/db/conf/chi/chi2001.html',
        'https://dblp.org/db/conf/chi/chi2000.html',
        'https://dblp.org/db/conf/chi/chi99.html', # so close to perfect consistency, but not quite.
        'https://dblp.org/db/conf/chi/chi98.html',
        'https://dblp.org/db/conf/chi/chi97.html',
        'https://dblp.org/db/conf/chi/chi96.html',
        'https://dblp.org/db/conf/chi/chi95.html',
        'https://dblp.org/db/conf/chi/chi1994.html',
        'https://dblp.org/db/conf/chi/chi1993.html',
        'https://dblp.org/db/conf/chi/chi92.html',
        'https://dblp.org/db/conf/chi/chi1991.html',
        'https://dblp.org/db/conf/chi/chi1990.html',
        'https://dblp.org/db/conf/chi/chi1989.html',
        'https://dblp.org/db/conf/chi/chi1988.html',
        'https://dblp.org/db/conf/chi/chi1987.html',
        'https://dblp.org/db/conf/chi/chi1986.html',
        'https://dblp.org/db/conf/chi/chi1985.html', 
        # 'https://dblp.org/db/conf/chi/chi1984.html', # there is no 1984 on dblp, I guess they skipped this year.
        'https://dblp.org/db/conf/chi/chi1983.html',
        'https://dblp.org/db/conf/chi/chi1982.html',
        'https://dblp.org/db/conf/chi/chi1981-1.html',
        'https://dblp.org/db/conf/chi/chi1981-2.html'
    ]

    simpleStructure = True
    i = 1
    for url in url_list:
        print('Processing (', i, ' of ', len(url_list), '): ', url)
        i += 1
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()

        page_html = mybytes.decode("utf8")
        fp.close()

        page_html = page_html.replace('<br />', '') # causes issues with soup's parsing.
        # <br />

        soup = BeautifulSoup(page_html, 'html.parser')

        publication_list_of_lists = soup.select('.publ-list')
        first = True
        for publication_list in publication_list_of_lists:
            # beautifulsoup, get number of children inside publication_list
            length = len(publication_list.contents)      
            if (length == 1):
                first = False
                continue
            for pub in publication_list.children:
                if first:
                    first = False
                    continue
                pub_info = parse_pub(pub)
                csv_string += pub_info + '\n'

    with open('chi.csv', 'w') as f:
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
        conference = 'CHI'
        abstract = ''
        award = ''
        return ','.join([conference, year, title, doi, abstract, authors_string, award])


if __name__ == '__main__':
    main()
    