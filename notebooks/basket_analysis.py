#!/usr/bin/env python
# coding: utf-8

# # Market Basket Analysis

# Based on https://github.com/chris1610/pbpython/blob/master/notebooks/Market_Basket_Intro.ipynb

# In[12]:


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_style('darkgrid')
random_state = 42
pd.set_option('display.float_format', lambda x: '%.3f' % x)

get_ipython().run_line_magic('matplotlib', 'inline')


# In[11]:


from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


# ## Prepare the data (skip if already prepared)

# In[3]:


get_ipython().run_cell_magic('time', '', '\nhours = [\'0\'+str(x)+\':00\' if x < 10 else str(x)+\':00\' for x in range(24)]\nhour_type = pd.CategoricalDtype(categories=hours, ordered=True)\n\ndtype={\'GUESTCHECKID\': object,\n       \'Date\': str,\n       \'HourName\': hour_type,\n       \'QuarterName\': "category",\n       \'GUESTCHECK_SalesNet\': np.float64,\n       \'GUESTCHECK_SalesTax\': np.float64,\n       \'Product\': "category",\n       \'FamilyGroup\': "category",\n       \'MajorGroup\': "category",\n       \'Product_SalesNet\': np.float64,\n       \'Product_SalesTax\': np.float64,\n       \'MPK\': object,\n       \'Restaurant\': object,\n       \'LocationType\': "category",\n       \'Concept\': "category",\n       \'ItemType\': "category",\n       \'ComboMealNum\': np.float64,\n       \'ile_razy\': np.float64,\n       \'SalesChannel\': "category"\n       }\nparse_dates = [\'Date\']\n\ndata = pd.read_csv(os.path.join(os.environ[\'DATA_PATH\'], \'kiosk_produkty/KIOSK_Produkty.csv\'), delimiter=";", thousands=\',\', error_bad_lines=False, dtype=dtype, parse_dates=parse_dates)')


# ### Create basket table

# In[4]:


# https://github.com/pandas-dev/pandas/issues/19136#issuecomment-380908428
def reset_index(df):
    '''Returns DataFrame with index as columns'''
    index_df = df.index.to_frame(index=False)
    df = df.reset_index(drop=True)
    #  In merge is important the order in which you pass the dataframes
    # if the index contains a Categorical. 
    # pd.merge(df, index_df, left_index=True, right_index=True) does not work
    return pd.merge(index_df, df, left_index=True, right_index=True)


# In[5]:


get_ipython().run_cell_magic('time', '', "basket = (data.groupby(['GUESTCHECKID', 'Product'])['ile_razy']\n          .sum().unstack())")


# In[ ]:


# Delete unnecesary data and save memory
del data


# In[ ]:


# Convert the units to 1 hot encoded values
def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1


# In[6]:


get_ipython().run_cell_magic('time', '', "basket = reset_index(basket).fillna(0).set_index('GUESTCHECKID').applymap(encode_units)")


# In[15]:


get_ipython().run_cell_magic('time', '', 'basket_sets = basket.applymap(encode_units)')


# In[ ]:


basket_sets.head()


# In[ ]:


get_ipython().run_cell_magic('time', '', "basket_sets.to_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets.csv'))")


# ## Load data (if prepared before)

# In[34]:


get_ipython().run_cell_magic('time', '', "basket_sets = pd.read_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets.csv'), index_col=0)")


# In[17]:


basket_sets.head()


# ### Basket analysis

# In[18]:


get_ipython().run_cell_magic('time', '', '# Build up the frequent items\nfrequent_itemsets = apriori(basket_sets, min_support=0.07, use_colnames=True)')


# In[19]:


frequent_itemsets.head()


# In[20]:


get_ipython().run_cell_magic('time', '', '# Create the rules\nrules = association_rules(frequent_itemsets, metric="lift", min_threshold=5)')


# #### Remove standard sets - related associations
# If someone buys Bsmart then we expect fries or sandwitch to be in the basket too. This associations are not interesting so we remove them.

# In[21]:


len(rules)


# In[31]:


rows_w_bsmart = (rules['antecedents'].astype(str).str.contains('Bsmart', regex=False) | rules['consequents'].astype(str).str.contains('Bsmart', regex=False))
rows_w_app_bucketfor1 = (rules['antecedents'].astype(str).str.contains('app_bucketfor1', regex=False) | rules['consequents'].astype(str).str.contains('app_bucketfor1', regex=False))
fillter_sets_out = (~rows_w_bsmart & ~rows_w_app_bucketfor1)


# In[32]:


len(rules[fillter_sets_out])


# In[40]:


pd.set_option('display.max_rows', 200)
rules[~rows_w_bsmart & ~rows_w_app_bucketfor1].sort_values('lift', ascending=False).head(20)


# In[39]:


rules.sort_values('lift', ascending=False).head(20)


# ### Conclusion
# - Looks like association analysis gives blurry image of the situation due to the obvious patterns that are very frequent:
#         - Bsmart: Fries, some main (longer, 2strips, iTwistB)
#         - app_bucketfor1: ex_45BitesAddon, app_bucketfor1, 2HotWings, DrumstickKent., fries, 
#         - etc
# - Solution could be in removing such obvious product combinations from the data by hand

# # Further cleaning

# ### Filtering data
# We will fillter out less popular products and those which are no actual products.

# In[43]:


limit = 1000
val_counts = data['Product'].value_counts()
less_popular_products = list(val_counts[val_counts < limit].index)
val_to_filter = ['Customer'] + less_popular_products


# In[45]:


len(val_counts)


# In[44]:


data_prod_filtered = data[~data['Product'].isin(val_to_filter)]


# In[ ]:


# Standard sets
{
'Bsmart': ['mStripsBsmart', 'mMiniTwistBsmart', 'mLongerBsmart', 'Fries', '2Strips', 'Longer', 'iTwistB']
'app_bucketfor1': ['DrumstickKent.','2HotWings','ex_45BitesAddon', 'Fries']
    
}

