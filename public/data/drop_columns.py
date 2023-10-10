# modified from https://www.geeksforgeeks.org/delete-a-csv-column-in-python/
import csv 

# 0 Conference
# 1 Year
# 2 Title
# 3 DOI
# 4 Link
# 5 FirstPage
# 6 LastPage
# 7 PaperType
# 8 Abstract
# 9 AuthorNames-Deduped
# 10 AuthorNames
# 11 AuthorAffiliation
# 12 InternalReferences
# 13 AuthorKeywords
# 14 AminerCitationCount
# 15 CitationCount_CrossRef
# 16 PubsCited_CrossRef
# 17 Award
with open("VIS_raw.csv", "r") as source: 
	reader = csv.reader(source) 
	with open("VIS.csv", "w") as result: 
		writer = csv.writer(result) 
		for r in reader: 
			writer.writerow((r[0], r[1], r[2], r[3], r[8], r[9], r[17]))
