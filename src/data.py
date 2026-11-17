# src/data.py
import time
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'presidential_election_data_1980_2024.csv'
YEARS = [1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]
DTYPES = {'Year': 'int', 'State': 'str', 'R Votes': 'int', 'D Votes': 'int',
          'D Raw Margin': 'float', 'D Adj Margin': 'float', 'D Adj Margin Swing': 'float'}


def scrape_year(year):
    """Scrape one election year and return a DataFrame with margins added."""
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
    start_row = next((i for i, s in enumerate(list_rows) if s.startswith('[Alabama')), None)
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
    
    df['D Raw Margin'] = 100*(df['D Votes']-df['R Votes'])/(df['D Votes']+df['R Votes'])
    national_margin = df.loc[df['State'] == 'Totals','D Raw Margin'].values[0]
    df['D Adj Margin'] = df['D Raw Margin'] - national_margin
    
    # Add a 'Year' column at the front to identify the data
    df.insert(0, 'Year', year)
    return df


def scrape_all():
    all_elections = []
    for year in YEARS:
        print(f"Scraping {year}...")
        all_elections.append(scrape_year(year))
        time.sleep(2)  # be polite to the server
    final_df = pd.concat(all_elections, ignore_index=True)
    final_df = final_df.sort_values(by=['State', 'Year'])
    final_df['D Adj Margin Swing'] = final_df.groupby('State')['D Adj Margin'].diff()
    return final_df


def load_data():
    """Load the cached CSV, scraping and saving it first if it doesn't exist."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, dtype=DTYPES)
    df = scrape_all()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df