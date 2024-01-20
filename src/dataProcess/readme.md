Processing Steps for VIS (rough draft partially from memory)

1. Wait until January for convenience.
   Note: Could do a few months earlier but would have to cross-check the early access publications with a list of published papers in VIS
2. Go to the Jan submission of TVCG at https://ieeexplore.ieee.org/
3. select all, manually deselect anythign that isn't a paper, e.g. front cover etc
4. export, citations, bibtex, citation and abstract.
   Note: may require multiple exports. set items per page to 100, should fit into only a few pages
5. run `python3 bib_to_csv.py` (currently requires setting filenames in .py)
6. Deduplication
   6a. (Preferred option), Get data from dblp, merge authornames with other csv with `merge_authors.py` script
   6b. If 6a is not possible run `python3 dedup-authors.py` (currently requires setting filenames in .py)
   Note: this can take some time since the API requires rate-limiting
   manually dedup ambiguous authors
7. manually add Test of time and best paper awards based on https://ieeevis.org/
8. run 'python3 combine.py' to combine with full paper dataset.
9. update paper stub creations
10. advertise
