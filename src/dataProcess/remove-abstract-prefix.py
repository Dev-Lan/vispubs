import csv 

INPUT_FILENAME = './eurovis.csv'
OUTPUT_FILENAME = './eurovis-prefix-removed.csv'
    
# 0 Conference
# 1 Year
# 2 Title
# 3 DOI
# 4 Abstract
# 5 AuthorNames-Deduped
# 6 Award

with open(INPUT_FILENAME, "r") as source: 
	reader = csv.reader(source)
	with open(OUTPUT_FILENAME, "w") as result:
		writer = csv.writer(result) 
		for r in reader: 
			print(r[1], r[3])
			abstract = r[4].removeprefix('Abstract')
			writer.writerow((r[0], r[1], r[2], r[3], abstract, r[5], r[6]))