import logging
from filter_dblp_xml import parse_large_xml_with_dtd
from parse_dblp_xml import dblp_to_csv
from filter_to_new import filter_to_new
from awards import add_awards
from abstracts import add_abstracts
from update_intermediate import update_intermediate
from filter_by_keywords import filter_to_vis_papers
from combine import combine
from process_paper_links import create_stub_files
from bulk_preprint_search import search_preprint_versions
from update_paper_link_flags import update_paper_link_flags
from update_changelog import update_changelog



def process_new_data_from_dblp():
  # Coarsly filter 4GB dblp xml file to only include potentially relevant files
  input_xml = './input/dblp.xml'
  input_dtd = './input/dblp-2023-06-28.dtd'
  filtered_xml = './temp/dblp_filtered.xml'
  step = 1
  print_banner(f"🦉 {step}. parse_large_xml_with_dtd")
  step += 1
  parse_large_xml_with_dtd(input_xml, input_dtd, filtered_xml)

  # Convert filtered dblp xml into CSV format and filter more precisely by conference
  potential_new_papers = './temp/potential_new_papers.csv'
  print_banner(f"🦉 {step}. dblp_to_csv")
  dblp_to_csv(filtered_xml, potential_new_papers)

  # Filter the potential new papers to only include the truly new ones
  new_papers = './temp/new_papers.csv'
  print_banner(f"🦉 {step}. filter_to_new")
  filter_to_new(potential_new_papers, new_papers)

  # Add awards information to the new papers
  award_filename = './input/awards.csv'
  new_papers_award = './temp/new_papers_award.csv'
  print_banner(f"🦉 {step}. add_awards")
  step += 1
  add_awards(award_filename, new_papers, new_papers_award)

  # Add abstracts to the new papers
  new_papers_award_abstract = './temp/new_papers_award_abstract.csv'
  print_banner(f"🦉 {step}. add_abstracts")
  step += 1
  add_abstracts(new_papers_award, new_papers_award_abstract)

  # Update the intermediate files with the new papers
  print_banner(f"🦉 {step}. update_intermediate")
  step += 1
  update_intermediate(new_papers_award_abstract)

  # Filter the intermediate files to only include visualization papers
  print_banner(f"🦉 {step}. filter_to_vis_papers")
  step += 1
  filter_to_vis_papers('./intermediate/chi.csv', './intermediate/chi-filtered.csv')

  # Combine all the filtered files into a single file
  print_banner(f"🦉 {step}. combine")
  step += 1
  combine()

  # Create stub files for any new paper resource pages
  print_banner(f"🦉 {step}. create_stub_files")
  step += 1
  create_stub_files()

  # Search for preprint versions of the papers
  print_banner(f"🦉 {step}. search_preprint_versions")
  step += 1
  search_preprint_versions()

  # Update the link flags column in the paper list
  print_banner(f"🦉 {step}. update_paper_link_flags")
  step += 1
  update_paper_link_flags()

  # Update the changelog file
  print_banner(f"🦉 {step}. update_changelog")
  step += 1
  update_changelog(new_papers_award_abstract)
  return

def print_banner(message):
  logger = logging.getLogger('main')
  logger.info('')
  logger.info(f"{'='*80}")
  logger.info(message)
  logger.info(f"{'='*80}")

def configure_logging():
  logging.basicConfig(level=logging.DEBUG,
                      format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                      datefmt='%m-%d %H:%M',
                      filename='./temp/data_ingestion.log',
                      filemode='w')
  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
  console.setFormatter(formatter)
  logging.getLogger().addHandler(console)

if __name__ == '__main__':
  configure_logging()
  process_new_data_from_dblp()

# UPDATE WORKFLOWS
# new data from dblp
  # get dblp xml snapshot
  # run main.py, review, deploy

# author submits homepage
  # manual, update authors.csv, update changelog.md, deploy

# Author submits resource links
  # update_paper_link_flags.py # to update the link flags column in paper list
  # update_changelog.py # add to changelog file

# Add early access papers
  # TBD
