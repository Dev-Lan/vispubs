import requests
import csv
import re
import time

INPUT_FILENAME = './temp/new_papers.csv'
OUTPUT_FILENAME = './temp/new_papers_abstract.csv'

def strip_xml_tags(text):
	'''Remove XML tags from a string'''
	clean = re.compile('<.*?>')
	return re.sub(clean, '', text)

def get_abstract_from_doi_crossref(doi):
	base_url = "https://api.crossref.org/works/"
	url = f"{base_url}{doi}"

	try:
		response = requests.get(url)
		response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
		result = response.json()
		abstract = result['message']['abstract']
		abstract = strip_xml_tags(abstract)
		# the string "Abstract" is sometimes prepended to the abstract
		abstract = abstract.removeprefix('Abstract')
		return abstract
	except Exception as e:
		print(f"Error fetching abstract for DOI {doi}: {e}")
		return None


def get_abstract_from_doi_semantic(doi):
	base_url = "https://api.semanticscholar.org/v1/paper/"
	url = f"{base_url}{doi}"

	try:
		response = requests.get(url)
		response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
		result = response.json()
		abstract = result['abstract']
		abstract = strip_xml_tags(abstract)
		return abstract
	except Exception as e:
		print(f"Error fetching abstract for DOI {doi}: {e}")
		return None

def replace_special_chars(text):
  '''Replace special characters in a string'''
  return text.replace('‐','-').replace('‘',"'").replace('’', "'").replace('“', '"').replace('”', '"').replace('…', '...')

def get_abstract_from_doi(doi):
	# sleep for 0.4 seconds to avoid rate limiting
	time.sleep(0.4)
	abstract = get_abstract_from_doi_semantic(doi)
	if abstract is None:
		abstract = get_abstract_from_doi_crossref(doi)
	if abstract is not None:
		abstract = replace_special_chars(abstract)
	return abstract

# 0 Conference
# 1 Year
# 2 Title
# 3 DOI
# 4 Abstract
# 5 AuthorNames-Deduped
# 6 Award
def add_abstracts(input_filename, output_filename):
	abstracts_found = 0
	abstracts_missing = 0
	with open(input_filename, "r") as source:
		reader = csv.reader(source)
		with open(output_filename, "w") as result:
			writer = csv.writer(result)
			for r in reader:
				print(r[1], r[3])
				if r[4] != '':
					abstract = r[4]
				else:
					abstract = get_abstract_from_doi(r[3])
					if abstract is None:
						print('\tskipped')
						abstracts_missing += 1
						abstract = ''
					else:
						print('\tfound')
						abstracts_found += 1
				writer.writerow((r[0], r[1], r[2], r[3], abstract, r[5], r[6]))
	print(abstracts_found, ' of ' , abstracts_missing + abstracts_found)

if __name__ == "__main__":
	add_abstracts(INPUT_FILENAME, OUTPUT_FILENAME)
