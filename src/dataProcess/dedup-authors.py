'''
This file loads an input csv file with an Authors column and a references csv file also with an authors column.
The column for both are formatted as "first1 last1; first2 last2; first3 last3" etc. However, the references file
has been deduplicated. So some authors have an id number after their name, e.g. "first1 last1 00001; first2 last2 00007".

This script will go through each author in the input file and check if they are in the references file. If they are,
it will replace the author name with the deduplicated version. Otherwise it will use the dblp api to try to find the
author. If the author is found, it will replace the author name with the deduplicated version.

If there is ambiguity in either approach, the file will add potential matches to the author name, and add
the DEDUP keword to the author name for manual review.
'''
import time
import csv
import requests
import xml.etree.ElementTree as ET


# Define the file paths
input_file_path = "./temp/VIS23/all-pubs.csv"
references_file_path = "../../public/data/papers.csv"
output_file_path = "./temp/VIS23/all-pubs-dedup.csv"
# TODO: Remove trailing whitespace on author names, maybe just update line 120, but test

# Load the input file
with open(input_file_path, "r") as input_file:
    input_data = list(csv.reader(input_file))
    # remove the header_row
    input_data.pop(0)

# Load the references file
with open(references_file_path, "r") as references_file:
    references_data = list(csv.reader(references_file))
    # remove the header_row
    references_data.pop(0)


dedup_lookup = dict()
for row in references_data:
    authors = row[5]
    for author in authors.split(";"):
        author = author.strip()
        if author == "":
            continue
        if author.split()[-1].isdigit():
            name = ' '.join(author.split()[:-1])
            key = author.split()[-1]
            if name not in dedup_lookup:
                dedup_lookup[name] = set()
            possible_keys = dedup_lookup[name]
            possible_keys.add(key)
        else:
            name = author
            if name not in dedup_lookup:
                dedup_lookup[name] = set()
            possible_keys = dedup_lookup[name]
            possible_keys.add(None)

# print(dedup_lookup['Stefan Bruckner'])
# print('Stefan Bruckner' in dedup_lookup)
# exit(1)
amiguous_vis_count = 0
ambiguous_dblp_count = 0
single_vis_count = 0
single_dblp_count = 0
no_dblp_count = 0

row_number = 0
for row in input_data:
    row_number += 1
    print()
    print('ROW: ' + str(row_number))
    authors = row[5]
    new_authors = []
    for author in authors.split(";"):
        author = author.strip()
        if author == "":
            continue
        if author in dedup_lookup:
            possible_keys = dedup_lookup[author]
            if len(possible_keys) == 1:
                single_vis_count += 1
                key = list(possible_keys)[0]
                if key is None:
                    new_authors.append(author)
                else:
                    new_authors.append(author + " " + list(possible_keys)[0])
            else:
                amiguous_vis_count += 1
                print("AMBIGUOUS AUTHOR NAME")
                print(author)
                print(possible_keys)
                new_authors.append(author + " TODO_DEDUP (" + '|'.join([str(k) for k in list(possible_keys)]) + ")")
        else:
            name_query = '+'.join([x + "$" for x in author.split()])
            query = "https://dblp.org/search/author/api?q=" + name_query
            print('fetching: ' + author)
            # fetch xml from dbpl api
            try:
                # sleep for 10 seconds to avoid rate limiting
                time.sleep(10)
                response = requests.get(query)
                response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
                result = response.text
                # Assume `result` is your XML string
                root = ET.fromstring(result)
                hits = root.find('hits')
                potential_matches = []
                for author in hits.findall('.//author'):
                    potential_matches.append(author.text)
                if len(potential_matches) == 0:
                    raise Exception("no author found")

                potential_author_name = '|'.join(potential_matches)
                result_count = len(potential_matches)
                if result_count > 1:
                    potential_author_name = "TODO_DEDUP " +potential_author_name
                    ambiguous_dblp_count += 1
                    print(("\tAMBIGUOUS AUTHOR NAME (DBLP): " + " (" + str(result_count) + ")\n\t" + potential_author_name))
                else:
                    single_dblp_count += 1
                new_authors.append(potential_author_name)
                
            except Exception as e:
                no_dblp_count += 1
                print(f"\tAPI returned error {author}: {e}")
                new_authors.append(author)
    row[5] = '; '.join(new_authors)



# open output file
with open(output_file_path, "w", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerow(['Conference', 'Year', 'Title', 'DOI', 'Abstract', 'AuthorNames-Deduped', 'Award'])
    for row in input_data:
        writer.writerow(row)

print('Conversion completed successfully.')

# print all count values
print(f"amiguous_vis_count: {amiguous_vis_count}")
print(f"ambiguous_dblp_count: {ambiguous_dblp_count}")
print(f"single_vis_count: {single_vis_count}")
print(f"single_dblp_count: {single_dblp_count}")
print(f"no_dblp_count: {no_dblp_count}")
total_count = amiguous_vis_count + ambiguous_dblp_count + single_vis_count + single_dblp_count + no_dblp_count

print(f"Percent ambiguous_vis_count: {(amiguous_vis_count + ambiguous_dblp_count) / float(total_count)}")