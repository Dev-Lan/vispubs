import csv
import bibtexparser

# Specify the file paths
bibtex_file_path = "temp/VIS23/all-pubs.bib"
csv_file_path = "temp/VIS23/all-pubs.csv"


def format_names(names):
    # converts a list of names in the format "last1, first1 and last2, first2" to "first1 last1; first2 last2"
    formatted_names = []
    for name in names.split(" and "):
        last, first = name.split(", ")
        formatted_names.append(first + " " + last)
    return "; ".join(formatted_names)

# Open the Bibtex file
with open(bibtex_file_path, "r") as bibtex_file:
    # Convert BibTeX to a structured object
    bib_database = bibtexparser.load(bibtex_file)


# Open the CSV file
with open(csv_file_path, "w", newline="") as csv_file:
    # Create a CSV writer
    writer = csv.writer(csv_file)

    # Write the header row
    writer.writerow(['Conference', 'Year', 'Title', 'DOI', 'Abstract', 'AuthorNames-Deduped', 'Award'])
    bib_items = entries = bib_database.entries
    # Write the data rows
    for item in bib_items:
        conference = 'EuroVis'
        year = item['year']
        title = item['title']
        # strip {} from start and end of title
        title = title.strip('{}')
        doi = item['doi']
        abstract = item['abstract'] if 'abstract' in item else ''
        authorNames = format_names(item['author'])
        award = ''
        writer.writerow([conference, year, title, doi, abstract, authorNames, award])

print("Conversion completed successfully.")
