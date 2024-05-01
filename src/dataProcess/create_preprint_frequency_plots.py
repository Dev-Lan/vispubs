import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

'''
This python script uses seaborn to generate three bar charts based on the data in three csv files.
- preprint_counts_and_frequencies_chi.csv
- preprint_counts_and_frequencies_vis.csv
- preprint_counts_and_frequencies_eurovis.csv

These csv files have three columns, only two are used for the bar chart, year, and frequency.
There should be one bar for each year, and the y axis should be the same for all three, with a max value of 1.0
'''


# Read the CSV files
df_chi = pd.read_csv('./temp/preprint_counts_and_frequencies_chi.csv')
df_vis = pd.read_csv('./temp/preprint_counts_and_frequencies_vis.csv')
df_eurovis = pd.read_csv('./temp/preprint_counts_and_frequencies_eurovis.csv')

# The first one is actually in 2007, but very low numbers aren't so interesting.
cutoff_year = 2012
df_chi = df_chi[df_chi['Year'] >= cutoff_year]
df_vis = df_vis[df_vis['Year'] >= cutoff_year]
df_eurovis = df_eurovis[df_eurovis['Year'] >= cutoff_year]

# change to percentage
df_chi['Frequencies'] *= 100
df_vis['Frequencies'] *= 100
df_eurovis['Frequencies'] *= 100

# Set the maximum y-axis value
max_value = 80

bar_color = '#3c859a'
width = 6
height = 4

# Create the bar charts
sns.barplot(x='Year', y='Frequencies', data=df_chi, color=bar_color)
sns.despine()
plt.ylim(0, max_value)
plt.xlabel('')
plt.ylabel('')
plt.title('CHI')
plt.yticks(range(20, max_value+1, 20))
plt.gca().set_yticklabels([str(int(val)) + '%' for val in plt.gca().get_yticks()])
plt.grid(axis='y', linestyle='-', alpha=1, color="white")
plt.tight_layout()
plt.gcf().set_size_inches(width, height)  # Adjust the figure size
plt.savefig('./temp/plot_chi')
plt.clf()

sns.barplot(x='Year', y='Frequencies', data=df_vis, color=bar_color)
sns.despine()
plt.ylim(0, max_value)
plt.xlabel('')
plt.ylabel('')
plt.title('')
plt.yticks(range(20, max_value+1, 20))
plt.gca().set_yticklabels([str(int(val)) + '%' for val in plt.gca().get_yticks()])
plt.grid(axis='y', linestyle='-', alpha=1, color="white")
plt.tight_layout()
plt.gcf().set_size_inches(width, height)  # Adjust the figure size
plt.savefig('./temp/plot_vis')
plt.clf()

sns.barplot(x='Year', y='Frequencies', data=df_eurovis, color=bar_color)
sns.despine()
plt.ylim(0, max_value)
plt.xlabel('')
plt.ylabel('')
plt.title('EuroVis')
plt.yticks(range(20, max_value+1, 20))
plt.gca().set_yticklabels([str(int(val)) + '%' for val in plt.gca().get_yticks()])
plt.grid(axis='y', linestyle='-', alpha=1, color="white")
plt.tight_layout()
plt.gcf().set_size_inches(width, height)  # Adjust the figure size
plt.savefig('./temp/plot_eurovis')
plt.clf()