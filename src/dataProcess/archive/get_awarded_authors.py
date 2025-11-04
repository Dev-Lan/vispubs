import csv

INPUT_PAPERS_FILENAME = "../../public/data/papers.csv"
INPUT_AUTHORS_FILENAME = "../../public/data/authors.csv"
OUTPUT_FILENAME = "./temp/top_authors.txt"
SAVE_TOP_AUTHORS = True
# 0 Conference
# 1 Year
# 2 Title
# 3 DOI
# 4 Abstract
# 5 AuthorNames-Deduped
# 6 Award

author_count = {}
with open(INPUT_PAPERS_FILENAME, "r") as source:
    reader = csv.reader(source)
    # skip first line
    next(reader)
    for r in reader:
        # print(r[1], r[3])
        authors = r[5].split(";")
        award = r[6].strip()
        if "BP" not in award:
            continue
        for a in authors:
            if a not in author_count:
                author_count[a] = 0
            author_count[a] += 1

author_set = set()
with open(INPUT_AUTHORS_FILENAME) as source:
    reader = csv.reader(source)
    # skip first line
    next(reader)
    for r in reader:
        author = r[0]
        author_set.add(author)

total_author_count = 0
covered_author_count = 0
for a in author_count:
    total_author_count += author_count[a]
    if a in author_set:
        covered_author_count += author_count[a]

# turn dict into list of tuples
author_count_list = []
for a in author_count:
    author_count_list.append((a, author_count[a]))

# sort by count
author_count_list.sort(key=lambda x: x[1], reverse=True)

print()
print("--------------------------")
print("Total unique authors:", len(author_count))
print("Covered unique authors:", len(author_set))
coverage_percentage = len(author_set) / len(author_count) * 100
formatted_percentage = "{:.2f}%".format(coverage_percentage)
print("Unique Coverage:", formatted_percentage)
print("--------------------------")
print("Total author instance count:", total_author_count)
print("Covered author instance count:", covered_author_count)
coverage_percentage = covered_author_count / total_author_count * 100
formatted_percentage = "{:.2f}%".format(coverage_percentage)
print("Instance Coverage:", formatted_percentage)
print("--------------------------")
# print('Top 5 unlinked authors:')
# printed = 0
# top_count = 0
# i = 0
# while printed < 5:
#     author, count = author_count_list[i]
#     i += 1
#     if author not in author_set:
#         print(author)
#         printed += 1
#         top_count += count
# print('Top 5 unlinked author count:', top_count, "({:.2f}%)".format(top_count / total_author_count * 100))
# print('--------------------------')
print()
if not SAVE_TOP_AUTHORS:
    exit()

with open(OUTPUT_FILENAME, "w") as result:
    writer = csv.writer(result)
    writer.writerow(["Author", "Count", "Done"])
    for author, count in author_count_list:
        done = "---X---" if author in author_set else ""
        writer.writerow([author, count, done])
