#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mechanicalsoup
import pandas as pd
import re
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import sqlite3


# In[2]:


browser = mechanicalsoup.StatefulBrowser()
url = "http://codeforces.com/problemset"


# In[3]:


def get_links(page: str):
    browser.open(urljoin(base_url, page))
    table = browser.page.select('.problems')[0]
    problems = table.find_all('tr')
    out = []
    for i in range(1, len(problems)):
        data = problems[i].find_all('td')[0:2]
        ida = data[0].a['href']
        difficulty = urlparse(ida).path.rpartition('/')[2]
        if not difficulty.isalpha():
            continue
        name = data[1].select('div:nth-child(1)')[0]
        tags = [tag.text for tag in data[1].select('div:nth-child(2)')[0].find_all('a')]
        out.append({
            'link': urljoin(base_url, ida),
            'difficulty': difficulty[0],
            'name': name.a.text.strip(),
            'tags': tags
        })
    return out


# In[4]:


resp = browser.open(url)
next_page_anchor = browser.page.find('a', text='→')
last_page_url = next_page_anchor.parent.parent.select('li:nth-last-child(2)')[0].span.a['href']
last_page = urljoin(url, last_page_url)
pattern = r'.+/(\d+)$'
lp = int(re.search(pattern, last_page).groups(1)[0])
base_url = urljoin(last_page, '.')


# In[5]:


scraped = []
for i in tqdm(range(1, lp + 1)):
    scraped.append(get_links(f'{i}'))


# In[6]:


df = pd.DataFrame(columns=['name', 'difficulty', 'link', 'tags'])
for page in scraped:
    links = pd.DataFrame(page, columns=['name', 'difficulty', 'link', 'tags'])
    links['tags'] = links['tags'].apply(lambda r: [re.sub(r'[^A-Za-z0-9 ]+', '', s).replace(' ', '_') for s in r])
    df = df.append(links)

df.head()


# In[7]:


df['contest'] = df.apply(lambda r: urlparse(r.link).path.rpartition('/')[0].rpartition('/')[2], axis=1)
df.head()


# In[8]:


df.to_csv('links.csv', index=False)


# In[9]:


dft = df.join(pd.get_dummies(df['tags'].apply(pd.Series).stack()).sum(level=0))
dft.drop('tags', axis=1, inplace=True)
dft = dft.convert_dtypes(convert_floating=True)
dft.head()


# In[20]:


conn = sqlite3.connect('./links.sqlite3')


# In[10]:


dft.to_sql('codeforces', conn, if_exists='replace')
conn.commit()


# In[13]:


tags = dft.columns.tolist()[3:]
tags


# In[22]:


pd.DataFrame(tags, columns=['tags']).to_sql('tags', conn, if_exists='replace')
conn.commit()
conn.close()

