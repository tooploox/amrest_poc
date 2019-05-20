#!/usr/bin/env python
# coding: utf-8

# # AmRest - pre POC analysis

# In[1]:


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_style('darkgrid')
pd.set_option('display.float_format', lambda x: '%.3f' % x)

get_ipython().run_line_magic('matplotlib', 'inline')


# ## Data preparation

# In[2]:


def load_sales_data():
    hours = ['0'+str(x)+':00' if x < 10 else str(x)+':00' for x in range(24)]
    hour_type = pd.CategoricalDtype(categories=hours, ordered=True)

    dtype={'GUESTCHECKID': object,
           'Date': str,
           'HourName': hour_type,
           'QuarterName': "category",
           'GUESTCHECK_SalesNet': np.float64,
           'GUESTCHECK_SalesTax': np.float64,
           'Product': "category",
           'FamilyGroup': "category",
           'MajorGroup': "category",
           'MPK': object,
           'Restaurant': object,
           'LocationType': "category",
           'Concept': "category",
           'ItemType': "category",
           'ComboMealNum': np.float64,
           'ile_razy': np.float64,
           'SalesChannel': "category"
           }
    parse_dates = ['Date']

    data = pd.read_csv(os.path.join(os.environ['DATA_PATH'],
                                    'kiosk_produkty/KIOSK_Produkty.csv'),
                       delimiter=";", thousands=',',
                       dtype=dtype,
                       parse_dates=parse_dates)
    return data


# In[3]:


get_ipython().run_cell_magic('time', '', 'data = load_sales_data()')


# In[4]:


data.info()


# #### Create yearn and month variable

# In[5]:


data['month'] = pd.DatetimeIndex(data['Date']).month


# In[6]:


data['year'] = pd.DatetimeIndex(data['Date']).year


# #### Convert to PLN Move comma so values correspond to PLN

# In[7]:


data['GUESTCHECK_SalesNet'] = data['GUESTCHECK_SalesNet'] / 1000000
data['GUESTCHECK_SalesTax'] = data['GUESTCHECK_SalesTax'] / 1000000
data['Product_SalesNet'] = data['Product_SalesNet'] / 1000000
data['Product_SalesTax'] = data['Product_SalesTax'] / 1000000


# In[8]:


id_columns = ['GUESTCHECKID', 'MPK', 'Restaurant']
categorical = ['Product', 'FamilyGroup', 'MajorGroup', 'LocationType', 'Concept', 'ItemType', 'SalesChannel']


# ## Data exploration

# In[9]:


get_ipython().run_cell_magic('time', '', 'data.describe()')


# In[10]:


data.head()


# In[11]:


limit = 100
for col in categorical:
    fig = plt.figure(figsize=(18,6))
    val_counts = data[col].value_counts()
    
    
    val_counts[:limit].plot.bar()
    plt.title(col + f" no of different values: {len(val_counts)}")
    plt.show()


# ### Legend
# 
# **LocationType/Concept**:
# - FC - Food Court (wspólna przestrzeń do jedzenia dla kilku restauracji, np. galerie handlowe)
# - FS -Free Stand (wolnostojący budynek, osobny, np. z Drive Thru)
# - ILM - In Line Mall (restauracja w ciągu np. W galerii, ale z osobną przestrzenią do jedzenia – tylko dla danej restauracji)
# - ILS - In Line Street (restauracja w ciągu sklepów, ale wejście od ulicy)
# - DT - Drive Thru
# 
# **ItemType**:
# - "2" - oznacza menu/zestaw 
# -  "1" - produkty składające się na dany zestaw.
# - "0" - produkt solo

# ### Conclusions
# 1. There is a large number of different products. Some of them should be treated differently like 'customer', 'coupon'.
# 2. 

# # Average cart size

# ## Mean cart size by category

# In[12]:


for col in categorical:
    display(data.groupby(col).mean().sort_values('GUESTCHECK_SalesNet', ascending=False).head(15))


# ## Date and time

# ### Year

# In[13]:


data.groupby('year').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.show()


# ### Month

# In[14]:


data[data['year']==2018.000].groupby('month').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.title("Average transaction value per month")
plt.show()


# In[15]:


data[data['year']==2019.000].groupby('month').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.title("Average transaction value per month")
plt.show()


# In[16]:


data.groupby('month').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.title("Average transaction value per month")
plt.show()


# ### Quarter of an hour

# In[17]:


data.groupby('QuarterName').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.show()


# No difference, as expected.

# ### Hour

# In[18]:


data.groupby('HourName').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.title("Average transaction value for a given hour")
plt.show()


# ### Date

# In[19]:


fig = plt.figure(figsize=(250,6))
data.groupby('Date').mean()['GUESTCHECK_SalesNet'].plot.bar()
plt.show()


# In[20]:


sales_by_day = data.groupby('Date').mean()


# #### Best days
# 
# We will explore best and worst days in the past in terms of guest checkout cart value. Maybe we will have some ideas about why on particular days people buy more or less.

# In[21]:


q = sales_by_day['GUESTCHECK_SalesNet'].quantile(0.95)
sales_by_day[sales_by_day['GUESTCHECK_SalesNet'] > q].sort_values('GUESTCHECK_SalesNet', ascending=False)


# #### Worst days

# In[22]:


q = sales_by_day['GUESTCHECK_SalesNet'].quantile(0.5)
sales_by_day[sales_by_day['GUESTCHECK_SalesNet'] < q].sort_values('GUESTCHECK_SalesNet')


# ## Popular items by concept type

# In[23]:


list(data['Concept'].unique())


# In[24]:


concept_types =[
'STANDARD',
 'DT STANDARD',
 'STANDARD+DT WIN',
 'DT MOP',
 'DT',
 'KIOSK',
 'FC',
 'DT LIGHT',
 'ILS']


# In[25]:


limit = 20
for conc in concept_types:
    fig = plt.figure(figsize=(18,6))
    val_counts = data[data['Concept']==conc]['Product'].value_counts()
    val_counts[3:limit].plot.barh()
    plt.title(conc + f" no of different values: {len(val_counts)}")
    plt.show()


# # Conclusion
# - It seems that in general difference between Kiosk and Drive Thru is that
#     - people generaly buy **smaller sets** sets in Kiosk like Bsmart
#     - people generally buy **larger sets** in Drive Thru like BucketFor1

# # TODOs

# ## Number of customers

# ## Average revenue

# ## Decision tree

# ## Dask

# In[157]:


get_ipython().system(' pip install dask[complete]')


# In[243]:


import dask.dataframe as dd


# In[244]:


get_ipython().run_cell_magic('time', '', 'df = dd.read_csv(data_path, delimiter=";", error_bad_lines=False)')


# In[ ]:




