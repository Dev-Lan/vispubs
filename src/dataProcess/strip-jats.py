import csv
import re

def strip_xml_tags(text):
	'''Remove XML tags from a string'''
	clean = re.compile('<.*?>')
	return re.sub(clean, '', text)

with open("papers.csv", "r") as source: 
	reader = csv.reader(source)
	with open("papers-abstract-cleaned.csv", "w") as result:
		writer = csv.writer(result) 
		for r in reader: 
			print(r[1], r[3])
			if r[4] == '':
				continue
			abstract = strip_xml_tags(r[4])

			writer.writerow((r[0], r[1], r[2], r[3], abstract, r[5], r[6]))