import pandas as pd

'''
Given a CSV file of new papers, update the corresponding intermediate file with the new papers.
The file it should be stored to is determined by the Conference column
- If the conference is Vis, the file is VIS.csv
- If the conference is EuroVis, the file is eurovis.csv
- If the conference is CHI, the file is chi.csv
'''
INPUT_FILENAME = './temp/new_papers_abstract.csv'


def main(input_filename):
  # Read the new papers CSV file
  new_papers = pd.read_csv(input_filename)

  # open all the possible output files
  folder = './intermediate/'
  vis = pd.read_csv(folder + 'VIS.csv')
  eurovis = pd.read_csv(folder + 'eurovis.csv')
  chi = pd.read_csv(folder + 'chi.csv')

  # facet new_papers by conference
  vis_new = new_papers[new_papers['Conference'] == 'Vis']
  eurovis_new = new_papers[new_papers['Conference'] == 'EuroVis']
  chi_new = new_papers[new_papers['Conference'] == 'CHI']

  # update the intermediate files
  vis_new = pd.concat([vis, vis_new])
  eurovis_new = pd.concat([eurovis, eurovis_new])
  chi_new = pd.concat([chi, chi_new])

  # Save the sorted dataframe to the output file
  vis_new.to_csv(folder + 'VIS.csv', index=False)
  eurovis_new.to_csv(folder + 'eurovis.csv', index=False)
  chi_new.to_csv(folder + 'chi.csv', index=False)

if __name__ == "__main__":
  main(INPUT_FILENAME)
