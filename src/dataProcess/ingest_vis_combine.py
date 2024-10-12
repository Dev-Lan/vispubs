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
from resource_ingestion import update_resources
from update_changelog import update_changelog



def process_new_data_from_dblp():
  step = 0

  # Update the intermediate files with the new papers
  step += 1
  print_banner(f"🦉 {step}. update_intermediate")
  update_intermediate('./temp/vis24.csv')

  # Combine all the filtered files into a single file
  step += 1
  print_banner(f"🦉 {step}. combine")
  combine() # TODO: new columns

  # Create stub files for any new paper resource pages
  step += 1
  print_banner(f"🦉 {step}. create_stub_files")
  create_stub_files()

  # Run the resource ingestion script
  step += 1
  print_banner(f"🦉 {step}. update_resources")
  update_resources('./temp/vis24_resources.csv')

  # Update the link flags column in the paper list
  step += 1
  print_banner(f"🦉 {step}. update_paper_link_flags")
  update_paper_link_flags()

  # Update the changelog file
  step += 1
  print_banner(f"🦉 {step}. update_changelog")
  update_changelog('./temp/vis24.csv')
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
