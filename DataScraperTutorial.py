import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
from urllib.request import urlopen
from bs4 import BeautifulSoup
#%matplotlib inline

url = "http://www.hubertiming.com/results/2017GPTR10K"
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')
rows = soup.find_all('tr')

list_rows = []
for row in rows:
    row_td = row.find_all('td')
    str_cells = str(row_td)
    cleantext = BeautifulSoup(str_cells, "lxml").get_text()
    list_rows.append(cleantext)

df = pd.DataFrame(list_rows)
df.head(10)


