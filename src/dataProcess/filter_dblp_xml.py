from os import close
from lxml import etree
import logging

'''
Used to filter large dblp xml file to only include relevant files.
'''

INPUT_XML = './input/dblp.xml'
INPUT_DTD = './input/dblp-2023-06-28.dtd'
OUTPUT_XML = './temp/dblp_filtered.xml'

def parse_large_xml_with_dtd(xml_file, dtd_file, output_filename):
    logger = logging.getLogger('parse_large_xml_with_dtd')
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

    output_file.write('<dblp>')

    for event, elem in context:

        if not dtd.validate(elem):  # Validate each element against the DTD
            continue

        if elem.tag not in venue_types:
            continue

        count += 1
        if count % 100_000 == 0:
            logger.info(f"{count / 1_000_000} M")

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

    output_file.write('</dblp>')

    output_file.close()

def test_entity_resolution(xml_file, dtd_file):
    logger = logging.getLogger('parse_large_xml_with_dtd')
    # Load the DTD
    with open(dtd_file, 'rb') as f:
        dtd = etree.DTD(f)

    # Load the XML
    parser = etree.XMLParser(dtd_validation=True, load_dtd=True)
    try:
        tree = etree.parse(xml_file, parser)
        logger.debug("Entity resolution works correctly.")
    except etree.XMLSyntaxError as e:
        logger.error("Error in entity resolution:")
        logger.error(e)

if __name__ == '__main__':
  parse_large_xml_with_dtd(INPUT_XML, INPUT_DTD, OUTPUT_XML)
