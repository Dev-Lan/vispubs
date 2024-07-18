from lxml import etree

def parse_large_xml_with_dtd(xml_file, dtd_file):
    # Load the DTD
    with open(dtd_file, 'rb') as f:
        dtd = etree.DTD(f)


    count = 0
    # Define a context for iteratively parsing the XML file
    context = etree.iterparse(xml_file, events=('end',), load_dtd=True, huge_tree=True)
    venue_types = set(['article', 'inproceedings', 'proceedings'])
    query_title = 'Using Exemplars to Visualize'
    query_author = 'Tobias Isenberg'
    for event, elem in context:
        if not dtd.validate(elem):  # Validate each element against the DTD
            continue
        if elem.tag not in venue_types:
            continue

        # check if th inner <title> element matches query_title
        title = elem.find('author')
        if title is not None and title.text is not None and query_author in title.text:
            # print(title.text)
            print(etree.tostring(elem, pretty_print=True).decode())
    
        # print('='*40)
        # print(count)
        # print('='*40)
        # print(etree.tostring(elem, pretty_print=True).decode())
        count += 1
        if count % 100_000 == 0:
            print(count / 1_000_000, 'M')
        # if count == 10:
        #     break
        # if elem.tag == "year" and elem.text == "1980":
        #     print("Found element with year 1980:", etree.tostring(elem, pretty_print=True).decode())

        # Clear the element to free memory
        # elem.clear()
        # while elem.getprevious() is not None:
        #     del elem.getparent()[0]


    del context  # Ensure all memory is freed

# Replace 'your_large_file.xml' and 'your_dtd_file.dtd' with your actual file paths
parse_large_xml_with_dtd('./input/dblp.xml', './input/dblp.dtd')


