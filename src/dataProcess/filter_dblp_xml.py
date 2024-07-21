from os import close
from lxml import etree

'''
Used to filter large dblp xml file to only include relevant files.
This is useful for developing changes and testing them on a smaller file.
'''

def parse_large_xml_with_dtd(xml_file, dtd_file, output_filename):
    # Load the DTD
    with open(dtd_file, 'rb') as f:
        dtd = etree.DTD(f)


    output_file = open(output_filename, 'w')

    count = 0
    # Define a context for iteratively parsing the XML file
    context = etree.iterparse(xml_file, events=('end',), load_dtd=True, huge_tree=True)
    vis_venues = set(['IEEE Trans. Vis. Comput. Graph.', 'Comput. Graph. Forum'])
    vis_conferences = set(['CHI', 'IEEE VIS (Short Papers)', 'EuroVis (Short Papers)'])

    venue_types = set(['article', 'inproceedings'])


    tag_count = 0
    last_tag = None

    for event, elem in context:

        if not dtd.validate(elem):  # Validate each element against the DTD
            continue

        if elem.tag not in venue_types:
            continue

        count += 1
        if count % 100_000 == 0:
            print(count / 1_000_000, 'M')

        journal = elem.find('journal')
        venue = elem.find('booktitle')

        journal_text = journal.text if journal is not None else ''
        venue_text = venue.text if venue is not None else ''
        if journal_text == '' and venue_text == '':
            continue

        if journal_text not in vis_venues and venue_text not in vis_conferences:
            continue

        # save elem to output file
        element_string = etree.tostring(elem, pretty_print=True).decode()
        output_file.write(element_string)

    output_file.close()

# Replace 'your_large_file.xml' and 'your_dtd_file.dtd' with your actual file paths
parse_large_xml_with_dtd('./input/dblp.xml', './input/dblp.dtd', './temp/vis_papers.xml')


