
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('darkgrid')
random_state = 42
pd.set_option('display.float_format', lambda x: '%.3f' % x)

get_ipython().run_line_magic('matplotlib', 'inline')


# In[8]:


data = pd.read_csv('../../data/KIOSK_Produkty.csv', sep='delimiter', header=None)


# In[ ]:


data.head()

