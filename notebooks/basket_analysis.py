#!/usr/bin/env python
# coding: utf-8

# # Market Basket Analysis - 'Product' level

# Based on https://github.com/chris1610/pbpython/blob/master/notebooks/Market_Basket_Intro.ipynb

# In[1]:


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

pd.set_option('display.float_format', lambda x: '%.3f' % x)

get_ipython().run_line_magic('matplotlib', 'inline')


# ## Load sales data

# In[2]:


def load_sales_data():
    hours = ['0'+str(x)+':00' if x < 10 else str(x)+':00' for x in range(24)]
    hour_type = pd.CategoricalDtype(categories=hours, ordered=True)

    dtype={'GUESTCHECKID': object,
           'Date': str,
           'HourName': hour_type,
           'QuarterName': "category",
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


# ## Analysis - 'Product' level
# We will create baskets of individual products and see if we can find some interesing relationships.

# ### Prepare basket data

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


# Convert the units to 1 hot encoded values
def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1


def create_basket_sets(data, variable):
    
    basket = (data.groupby(['GUESTCHECKID', variable])['ile_razy']
          .sum().unstack())
    
    basket = reset_index(basket).fillna(0).set_index('GUESTCHECKID').applymap(encode_units)
    
    basket_sets = basket.applymap(encode_units)
    
    return basket_sets


# In[ ]:


get_ipython().run_cell_magic('time', '', "basket_sets = create_basket_sets(data, 'Product')")


# In[24]:


get_ipython().run_cell_magic('time', '', "basket_sets.to_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets_product.csv'))")


# ### Load data

# In[2]:


get_ipython().run_cell_magic('time', '', "basket_sets = pd.read_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets_product.csv'), index_col=0)")


# In[90]:


basket_sets = basket_sets.drop(columns=['Customer'])


# In[91]:


basket_sets.head()


# ### Create basket rules

# In[107]:


def analyze_basket(basket_sets):
    # Build up the frequent items
    frequent_itemsets = apriori(basket_sets, min_support=0.005, use_colnames=True)
    
    display(frequent_itemsets.sort_values('support', ascending=False).head(25))
    
    # Create the rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    
    return rules


# In[ ]:


get_ipython().run_cell_magic('time', '', 'rules = analyze_basket(basket_sets)')


# ### Explore basket rules

# #### Metric explanations
# - Say, that lift for an association rule “if Toast then Coffee” is 1.48 because the confidence is 70%. This means that consumers who purchase Toast are 1.48 times more likely to purchase Coffee than randomly chosen customers. Larger lift means more interesting rules. Association rules with high support are potentially interesting rules. Similarly, rules with high confidence would be interesting rules as well.

# In[ ]:


rules_sic = rules[~rules['consequents'].astype(str).str.contains(',', regex=False)]
print(f"Total number of rules found: {len(rules)} Number of rules with single item consequents: {len(rules_sic)} ")
rules = rules_sic


# In[ ]:


rules = rules[~(rules['consequents'].astype(str).str.contains('Fries', regex=False) |
                rules['consequents'].astype(str).str.contains('LargeFries', regex=False) |
                rules['consequents'].astype(str).str.contains('PepsiRefill', regex=False)
               )]


# In[ ]:


rules.query('4 >lift > 1.2 and confidence > 0.3').sort_values('lift', ascending=False).head(300)


# ### Remove standard sets - related associations
# Example: If someone buys Bsmart then we expect fries or sandwitch to be in the basket too.
# 
# Those kinds of associations are not interesting and we will remove them.

# In[110]:


def phrase_filter(rules, phrase):
    rows_w_phrase = (rules['antecedents'].astype(str).str.contains(phrase, regex=False) | rules['consequents'].astype(str).str.contains(phrase, regex=False))
    
    return (rows_w_phrase)


# In[111]:


len(rules)


# In[112]:


fillter = (~phrase_filter(rules, 'Bsmart') & ~phrase_filter(rules, 'app_bucketfor1') & ~phrase_filter(rules, 'ex_45BitesAddon'))
display(len(rules[fillter]))
rules[fillter].sort_values('lift', ascending=False).head(50)


# #### Conclusions
# - Looks like association analysis gives blurry image of the situation due to the obvious patterns that are very frequent:
#         - Bsmart: Fries, some main (longer, 2strips, iTwistB)
#         - app_bucketfor1: ex_45BitesAddon, app_bucketfor1, 2HotWings, DrumstickKent., fries, 
#         - etc
# - Solution could be in removing such obvious product combinations from the data by hand

# ### TODO:  Filtering data
# We will fillter out less popular products and those which are no actual products.

# In[13]:


limit = 1000
val_counts = data['Product'].value_counts()
less_popular_products = list(val_counts[val_counts < limit].index)
val_to_filter = ['Customer'] + less_popular_products


# In[14]:


len(val_counts)


# In[15]:


data_prod_filtered = data[~data['Product'].isin(val_to_filter)]


# In[18]:


# Standard sets
{'Bsmart': ['mStripsBsmart', 'mMiniTwistBsmart', 'mLongerBsmart', 'Fries', '2Strips', 'Longer', 'iTwistB'],
'app_bucketfor1': ['DrumstickKent.','2HotWings','ex_45BitesAddon', 'Fries']
}


# ## Analysis - 'FamilyGroup' level

# In[19]:


# Delete unnecesary data and save memory
del basket_sets


# ### Prepare basket data

# In[20]:


get_ipython().run_cell_magic('time', '', "basket_sets = create_basket_sets(data, 'FamilyGroup')")


# In[21]:


get_ipython().run_cell_magic('time', '', "basket_sets.to_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets_familygroup.csv'))")


# In[25]:


get_ipython().run_cell_magic('time', '', "# Load data (if prepared before)\nbasket_sets = pd.read_csv(os.path.join(os.environ['DATA_PATH'], 'basket_sets/basket_sets_familygroup.csv'), index_col=0)")


# In[23]:


basket_sets.head()


# ### Create basket rules

# In[79]:


get_ipython().run_cell_magic('time', '', 'rules = analyze_basket(basket_sets)')


# ### Explore basket rules

# In[80]:


basket_sets.columns.values


# In[81]:


len(rules)


# In[82]:


pd.set_option('display.max_rows', 300)
fillter = (~phrase_filter(rules, 'Promos'))
rules[fillter].sort_values('lift', ascending=False)


# In[77]:


rules.sort_values('lift', ascending=False).head(20).head()


# In[33]:


display(rules[phrase_filter(rules,'Cold Beverages')].head())


# In[36]:


display(rules[phrase_filter(rules,'Salads')].head())


# #### Conclusions

# - some obvious associacions can be found when not filtering data. It is not surprising that people who bought chicken, they migh also buy fries or cold beverage.
# - it is somehow interesting that people who bought:
#     - chicken are 2x likely to buy salad
# 
# 
# In the next step we would like to explore less popular groups of products like hot beverages, desserts, salads.

# #### Keep carts with at least one item buought in category: hot beverages, desserts, salads, 'Breakfast', 'LSM'

# In[50]:


product_groups = ['Hot Beverages', 'Desserts', 'Salads', 'Breakfast', 'LSM']
rules = analyze_basket(basket_sets[(basket_sets[product_groups] !=0).any(1)])


# In[51]:


rules.head()


# In[53]:


for product in product_groups:
    display(product)
    display(rules[phrase_filter(rules,product)].sort_values('lift', ascending=False).head(50))


# #### Conclusions
# 

# - **Some products groups are special**
#     - Desserts, hot beverages or salads are rarely sold by themselves. Customers who already bought other items adds those to the cart. 
#     - Desserts are usually bought when customer is having a coupon or if there is a promotion for it.
# - **Juice with chicken nuggets**.
#     - Orange juice is common next choice when someone buys chicken bites (nuggets).
# - It might make sense to recommend dessert purchase, only when user already selected several other items or a hot beverage. We could recommend orange juice when it is likely that customers are parents. It seems that some product groups are an “extra” thing to buy, but never the main reason to enter restaurant, so there is little point in exposing them heavily at the early stage. 
# 
