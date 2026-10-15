import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import urlopen
from bs4 import BeautifulSoup
#%matplotlib inline

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5


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
df1 = df[0].str.split(',', expand=True)
#print(df1.head(10))

col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)
#print(all_header)

df2 = pd.DataFrame(all_header)
df3 = df2[0].str.split(',', expand=True)
frames = [df3, df1]
df4 = pd.concat(frames)
df5 = df4.dropna(axis=0, how='any')
df5.loc[:,0] = df5[0].str.strip('[')
df5.loc[:,8] = df5[8].str.strip(']')
for i in range(9):
    df5.loc[:,i] = df5[i].str.strip()
#print(df5.head())
df6 = df5.rename(columns=df5.iloc[0])
df7 = df6.drop(df6.index[0])
#print(df7.head())

time_list = df7['Time'].tolist()
time_mins = []
for i in time_list:
    isplit = i.split(':')
    if len(isplit) == 2:
        m, s = i.split(':')
        math = (int(m) * 60 + int(s))/60
        time_mins.append(math)
    elif len(isplit) == 3:
        h, m, s = i.split(':')
        math = (int(h) * 3600 + int(m) * 60 + int(s))/60
        time_mins.append(math)
    else:
        print("Error: Unexpected time split length = "+str(len(isplit)))
#print(time_mins[:10])

df7['Runner_mins'] = time_mins
#print(df7.describe(include=[np.number]))

#df7.boxplot(column='Runner_mins')
#plt.grid(True, axis='y')
#plt.ylabel('Chip Time')
#plt.xticks([1], ['Runners'])
#plt.show()

#x = df7['Runner_mins']
#ax = sns.histplot(x, kde=True, color='m', bins=25)
#plt.show()

#f_fuko = df7.loc[df7['Gender']=='F']['Runner_mins']
#m_fuko = df7.loc[df7['Gender']=='M']['Runner_mins']
#sns.histplot(f_fuko, kde=True, label='Female')
#sns.histplot(m_fuko, kde=True, label='Male')
#plt.legend()
#plt.show()

#g_stats = df7.groupby("Gender", as_index=True).describe()
#print(g_stats)

df7.boxplot(column='Runner_mins', by='Gender')
plt.ylabel('Time')
plt.suptitle("")
plt.show()