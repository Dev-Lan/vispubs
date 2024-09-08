get new dblp data (handle early access papers)
'''
filter_dblp_xml.py # filters 4GB dblp xml to pubs from relevant files
parse_dblp_xml.py # converts filtered dblp xml into csv and filters out some by conference
- filter_to_new.py # filters csv to only the new files, based on the existing papers.csv
abstracts.py # finds the abstracts for the new potential files
add_to_conference_files.py # adds the new papers into repective conf files
  - reuse filter_by_keywords.py for the filtered versions

merge the intermediate files (combine with prev)
  the rest operate on full file

- awards.py # incorporate awards
process_paper_links.py # to create stubs for any new paper resource file pages
bulk_preprint_search.py # search for preprints
update_paper_link_flags.py # to update the link flags column in paper list
update_changelog.py # add to changelog file
'''

author submits homepage
update_changelog.py # add to changelog file


Author submits resource links
update_paper_link_flags.py # to update the link flags column in paper list
update_changelog.py # add to changelog file



Add early access papers
