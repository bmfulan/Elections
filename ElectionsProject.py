# %% setup: imports and load data
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import urlopen
from bs4 import BeautifulSoup
#import requests
import time

#from pylab import rcParams
#rcParams['figure.figsize'] = 15, 5
pd.set_option('display.max_rows', None)

# Define your local file name
CACHE_FILE = 'presidential_election_data_1980_2024.csv'

# Check if the data already exists locally
if os.path.exists(CACHE_FILE):
    print(f"Local cache found! Loading data from {CACHE_FILE}...")
    
    # Read the CSV. We explicitly tell pandas to preserve our Int64 types 
    # since standard CSVs otherwise revert columns with NaNs back to floats.
    final_df = pd.read_csv(CACHE_FILE, dtype={
        'Year': 'int', 'State': 'str', 'R Votes': 'int', 'D Votes': 'int', 'D Raw Margin': 'float',
        'D Adj Margin': 'float', 'D Adj Margin Swing': 'float'
    })

else:
    print("No local cache found. Initiating web scraper...")

    # Define the election years and initialize a master list
    years = [1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]
    all_elections = []

    for year in years:
        print(f"Scraping data for {year}...")
    
        url = f"https://www.presidency.ucsb.edu/statistics/elections/{year}"
        html = urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find_all('tr')
    
        list_rows = []
        for row in rows:
            row_td = row.find_all('td')
            str_cells = str(row_td)
            cleantext = BeautifulSoup(str_cells, "lxml").get_text()
            list_rows.append(cleantext)
        #print(list_rows)
        start_row = next((i for i, s in enumerate(list_rows) if s.startswith('[Alabama')), None)
        #print(start_row)
        end_row = next((i for i, s in enumerate(list_rows) if s.startswith('[Totals')), None)
        list_rows2 = list_rows[start_row:end_row-1]+list_rows[end_row:end_row+1]

        df = pd.DataFrame(list_rows2)
        df_series = df[0].str.strip('[]')
        df = df_series.str.split(', ', expand=True)
        df = df[[0,2,5]].copy()
        df = df.replace(',', '', regex=True)
        df = df.replace('\*', '', regex=True)
        df = df.replace('Dist. of Col.', 'District of Columbia', regex=True)
        if year in [1980, 1984, 1988, 2000, 2004]:
            df.columns = ['State','R Votes','D Votes']
        else:
            df.columns = ['State','D Votes','R Votes']
        df = df[~df['State'].isin(['CD-1','CD-2','CD-3'])]
        df = df.astype({'D Votes': int, 'R Votes': int})
        #print(df.head(10))
        
        df['D Raw Margin'] = 100*(df['D Votes']-df['R Votes'])/(df['D Votes']+df['R Votes'])
        national_margin = df.loc[df['State'] == 'Totals','D Raw Margin'].values[0]
        df['D Adj Margin'] = df['D Raw Margin'] - national_margin
        #print(df)
        
        # Add a 'Year' column at the front to identify the data
        df.insert(0, 'Year', year)
        
        # Append the cleaned year data to the master list
        all_elections.append(df)
        
        # Pause for 2 seconds to be polite to the UCSB servers
        time.sleep(2)

    # Concatenate all individual DataFrames into one final dataset
    final_df = pd.concat(all_elections, ignore_index=True)

    # Sort by state and then chronologically for each state
    final_df = final_df.sort_values(by=['State', 'Year'])

    # Group by state, then calculate the difference from the previous row
    final_df['D Adj Margin Swing'] = final_df.groupby('State')['D Adj Margin'].diff()

    # Show the final dataset by state
    for i in range(52):
        print(final_df.iloc[12*i:12*i+12])

    # Save the final dataset to a CSV file
    # index=False prevents pandas from writing the row numbers as a new column
    final_df.to_csv(CACHE_FILE, index=False)
    print(f"Scraping complete. Data successfully saved to {CACHE_FILE}")

# Remove "Totals" entries and entries from 1980 for margin swing analysis
final_df_states = final_df[final_df['State'] != 'Totals'].copy()
final_df_states_swing = final_df_states[final_df_states['Year'] != 1980].copy()

# Shift the swing column down by 1 row within each state's group
final_df_states_swing['Previous Swing'] = final_df_states_swing.groupby('State')['D Adj Margin Swing'].shift(1)



# %% autocorrelation by year

# Drop 1980, 1984, 1988 in order to create clean visual with 9 subplots in 3x3 grid
autocorr_df_grid = final_df_states_swing[~final_df_states_swing['Year'].isin([1980,1984,1988])].copy()

correlation = autocorr_df_grid['Previous Swing'].corr(autocorr_df_grid['D Adj Margin Swing'])

# Create the empty grid FIRST
g = sns.FacetGrid(
    data=autocorr_df_grid,
    col='Year',        # Split into separate charts by year
    col_wrap=3,          # Max 3 charts per row
    height=2.6,
    aspect=1.2,
    sharex=False,
    sharey=False
)

# Expand the axis limits on all empty charts BEFORE drawing the lines
g.set(xlim=(-15, 15), ylim=(-15, 15))

# NOW draw the regression lines and scatter points
# Because the axes are already -15 to 15, truncate=False will fill the entire space
g.map_dataframe(
    sns.regplot,
    x='Previous Swing',
    y='D Adj Margin Swing',
    ci=None,
    truncate=False,
    scatter_kws={'alpha': 0.5, 'color': 'purple', 'edgecolor': 'w'},
    line_kws={'color': 'black', 'linewidth': 2}
)

# Iterate through the dictionary of axes (key = Year, value = matplotlib Axis)
for year, ax in g.axes_dict.items():
    year = int(year)
    
    # Construct and apply the dynamic labels
    ax.set_xlabel(f"{year - 8}-{year - 4} Swing (%)", fontsize=10)
    ax.set_ylabel(f"{year - 4}-{year} Swing (%)", fontsize=10)
    
    # Clean up the title to just show the focal election year
    ax.set_title(f"{year} Election", weight='bold')
    
    # Add zero-line crosshairs
    ax.axhline(0, color='gray', linestyle='--', linewidth=1)
    ax.axvline(0, color='gray', linestyle='--', linewidth=1)

# Create a custom function to calculate and print the 'r' value inside the plot
def annotate_corr(data, **kws):
    # Calculate correlation for this specific facet's data
    r = data['Previous Swing'].corr(data['D Adj Margin Swing'])
    
    # Get the current matplotlib axis
    ax = plt.gca()
    
    # Place text in the top-left corner using relative axis coordinates (0 to 1)
    ax.text(0.05, 0.85, f"r = {r:.2f}", transform=ax.transAxes, 
            fontsize=11, weight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# Map the custom function across all facets
g.map_dataframe(annotate_corr)

# Clean up layout
g.figure.subplots_adjust(top=0.9, hspace=0.6, wspace=0.6) # hspace adds vertical room for the inner labels, wspace adds horizontal
g.figure.suptitle(f"Year-by-Year State Swing Autocorrelation; Overall Autocorrelation: r = {correlation:.2f}", fontsize=16, weight='bold')

#plt.tight_layout()
plt.show()



# %% autocorrelation overall

# Drop rows with NaNs (1980 and 1984 will be dropped since they lack a previous swing)
autocorr_df = final_df_states_swing.dropna(subset=['Previous Swing', 'D Adj Margin Swing'])

# Calculate the Pearson correlation coefficient
correlation = autocorr_df['Previous Swing'].corr(autocorr_df['D Adj Margin Swing'])
print(f"Overall Lag-1 Correlation: {correlation:.4f}")

plt.figure(figsize=(10, 8))

# Generate the scatter plot and linear regression trendline
sns.regplot(
    data=autocorr_df, 
    x='Previous Swing', 
    y='D Adj Margin Swing',
    scatter_kws={'alpha': 0.4, 'color': 'purple', 'edgecolor': 'w'}, 
    line_kws={'color': 'black', 'linewidth': 2}
)

# Add the zero-line crosshairs to create the 4 quadrants
plt.axhline(0, color='black', linestyle='--', linewidth=1.5)
plt.axvline(0, color='black', linestyle='--', linewidth=1.5)

# Annotate the 4 quadrants so the chart is instantly readable
bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)

plt.text(-20, 20, 'Reversion:\nSwung Rep, Bounced Dem', ha='center', bbox=bbox_props)
plt.text(20, -20, 'Reversion:\nSwung Dem, Bounced Rep', ha='center', bbox=bbox_props)
plt.text(20, 20, 'Momentum:\nSwung Dem, Continued Dem', ha='center', bbox=bbox_props)
plt.text(-20, -20, 'Momentum:\nSwung Rep, Continued Rep', ha='center', bbox=bbox_props)

# Format axes and titles
plt.title(f"Election Swings: Momentum vs. Reversion (r = {correlation:.2f})", fontsize=14)
plt.xlabel("Previous Election Swing (%)")
plt.ylabel("Current Election Swing (%)")

plt.tight_layout()
plt.show()



# %% Wisconsin: raw vs adjusted margin
wi = final_df_states[final_df_states['State'] == 'Wisconsin']

# Reshape from wide (two margin columns) to long (one 'Measure' column, one value column)
wi_long = wi.melt(
    id_vars='Year',
    value_vars=['D Raw Margin', 'D Adj Margin'],
    var_name='Measure',
    value_name='Margin (percentage points)'
)

wi_long['Measure'] = wi_long['Measure'].replace({
    'D Raw Margin' : 'Democratic Raw Margin',
    'D Adj Margin' : 'Democratic Adjusted Margin'
})

plt.figure(figsize=(10, 6))
ax = sns.lineplot(
    data=wi_long,
    x='Year',
    y='Margin (percentage points)',
    hue='Measure',
    marker='o',
    linewidth=2
)

# Shade the gap between the two lines (this gap is the national margin each year)
ax.fill_between(wi['Year'], wi['D Raw Margin'], wi['D Adj Margin'], alpha=0.12, color='gray')

# Zero line: above = Democratic, below = Republican
ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)

ax.set_xticks(sorted(wi['Year'].unique()))
ax.tick_params(axis='x', rotation=45)
ax.set_title("Wisconsin: Raw vs. Adjusted Democratic Two-Party Margin, 1980-2024")
plt.tight_layout()
plt.show()



# %% swing states adj margin

# Define the list of swing states
swing_states = ['Arizona', 'Georgia', 'Michigan', 'Nevada', 'North Carolina', 'Pennsylvania', 'Wisconsin']

# Filter the master DataFrame to only include these states
final_df_swing_states = final_df_states[final_df_states['State'].isin(swing_states)].copy()
# clean up dataframe names!!!

# Configure the visualization canvas
plt.figure(figsize=(12, 7))

# Generate the line plot
# 'hue' groups the data by State and assigns unique colors
# 'marker="o"' adds dots at each specific election year
sns.lineplot(
    data=final_df_swing_states, 
    x='Year', 
    y='D Adj Margin', 
    hue='State', 
    marker='o',
    linewidth=2,
    palette='tab10'  # A color palette with distinct, high-contrast colors
)

# Add a reference line at 0 to show who won the two-party vote in that state
plt.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)

# Format the axes and legend
plt.title("Democratic Two-Party Vote Margin (%) in Modern Swing States (1980-2024)", fontsize=14)
plt.ylabel("Democratic Two-Party Vote Margin")
plt.xlabel("Election Year")

# Ensure the x-axis displays ticks for every 4 years rather than arbitrary decimals
years = sorted(final_df_swing_states['Year'].unique())
plt.xticks(years, rotation=45) 

# Move the legend outside the plot so it doesn't cover the data lines
plt.legend(title='State', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout to fit the external legend
plt.tight_layout()
plt.show()



# %% state & year summaries

# Create a summary DataFrame for all states
# .agg() allows you to calculate multiple statistics at once
state_summary = final_df_states_swing.groupby('State')['D Adj Margin Swing'].agg(['mean', 'std']).reset_index()

# Rename columns for clarity
state_summary.columns = ['State', 'D Adj Margin Swing Mean', 'D Adj Margin Swing StdDev']
print(state_summary)

# Add the absolute swing (magnitude) to the master DataFrame
final_df_states_swing['Abs Adj Margin Swing'] = final_df_states_swing['D Adj Margin Swing'].abs().copy()

# Create a summary DataFrame for all years
year_summary = final_df_states_swing.groupby('Year')['Abs Adj Margin Swing'].agg(['mean', 'std']).reset_index()
year_summary.columns = ['Year', 'Abs Adj Margin Swing Mean', 'Abs Adj Margin Swing StdDev']
print(year_summary)



# %% heatmap adj margin

# Remove DC since it skews the colors
final_df_states = final_df_states[final_df_states['State'] != 'District of Columbia'].copy()

# Pivot the long-format data into a wide matrix for the heatmap
heatmap_data = final_df_states.pivot(index='State', columns='Year', values='D Adj Margin')

# Configure the visualization canvas
plt.figure(figsize=(12, 13.5))

# Generate the heatmap
# 'RdBu' maps negative numbers to Red (Republican swing) and positive to Blue (Dem swing)
sns.heatmap(
    heatmap_data, 
    cmap='RdBu', 
    center=0,          # Anchors the color white at exactly 0.0 swing
    annot=True,        # Displays the actual numeric value in the cell
    fmt=".3f",         # Formats the decimal places
    linewidths=0.5     # Adds gridlines between cells
)

plt.title("State-by-State Democratic Adjusted Margin, 1980-2024")
plt.xlabel("Election Year")
plt.ylabel("State")
plt.tight_layout()
plt.show()



# %% heatmap adj margin swing

# Pivot the long-format data into a wide matrix for the heatmap
heatmap_data = final_df_states.pivot(index='State', columns='Year', values='D Adj Margin Swing')

# Drop the year 1980 since its diff() values are all NaN
if 1980 in heatmap_data.columns:
    heatmap_data = heatmap_data.drop(columns=[1980])

# Configure the visualization canvas
plt.figure(figsize=(12, 13.5))

# Generate the heatmap
# 'RdBu' maps negative numbers to Red (Republican swing) and positive to Blue (Dem swing)
sns.heatmap(
    heatmap_data, 
    cmap='RdBu', 
    center=0,          # Anchors the color white at exactly 0.0 swing
    annot=True,        # Displays the actual numeric value in the cell
    fmt=".3f",         # Formats the decimal places
    linewidths=0.5     # Adds gridlines between cells
)

plt.title("State-by-State Democratic Adjusted Margin Swing, 1980-2024")
plt.xlabel("Election Year")
plt.ylabel("State")
plt.tight_layout()
plt.show()



# %% 2024 lollipop chart

df_sorted = final_df_states[final_df_states['Year'] == 2024]
df_sorted = df_sorted.sort_values(by='D Adj Margin')

# Assuming df_sorted is your dataframe and already sorted by 'D Margin'
states = df_sorted['State'].values
margins = df_sorted['D Adj Margin'].values

# Use numeric y-positions for the 51 entities (50 states + DC)
y_pos = np.arange(len(states))

# Create masks for the positive (Blue) and negative/zero (Red) values
is_dem = margins > 0
is_rep = margins <= 0

# Create a figure that is taller than it is wide to accommodate all labels
fig, ax = plt.subplots(figsize=(8, 12))

# Draw the horizontal stem lines starting from 0 to the margin value
ax.hlines(y=y_pos[is_dem], xmin=0, xmax=margins[is_dem], color='blue', linewidth=1.5)
ax.hlines(y=y_pos[is_rep], xmin=0, xmax=margins[is_rep], color='red', linewidth=1.5)

# Draw the filled circle markers at the end of each stem
ax.plot(margins[is_dem], y_pos[is_dem], 'bo')  # Blue circles
ax.plot(margins[is_rep], y_pos[is_rep], 'ro')  # Red circles

# Draw the solid black baseline at x=0
ax.axvline(x=0, color='black', linewidth=1.5)

# Format the Y-axis to display the state names
ax.set_yticks(y_pos)
ax.set_yticklabels(states, fontsize=9)

# Format the X-axis and overall chart properties
ax.set_xlabel("Democratic Margin (%)")
ax.set_title("2024 Adjusted Democratic Vote Margin by State")
ax.grid(axis='x', linestyle='--', alpha=0.7)

# Adjust padding so the state labels are not cut off
plt.tight_layout()
plt.show()