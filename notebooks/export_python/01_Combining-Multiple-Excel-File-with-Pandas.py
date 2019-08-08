#!/usr/bin/env python
# coding: utf-8

# # Introduction

# One of the most common tasks for pandas and python is to automate the process to aggregate data from multiple spreadsheets and files.
# 
# This article will walk through the basic flow required to parse multiple excel files, combine some data, clean it up and analyze it.
# 
# Please refer to [this post](http://pbpython.com/excel-file-combine.html) for the full post.

# # Collecting the Data

# Import pandas and numpy

# In[1]:


import pandas as pd
import numpy as np


# Let's take a look at the files in our input directory, using the convenient shell commands in ipython.

# In[3]:


get_ipython().system('ls ../data')


# There are a lot of files, but we only want to look at the sales .xlsx files.

# In[4]:


get_ipython().system('ls ../data/sales-*-2014.xlsx')


# Use the python glob module to easily list out the files we need

# In[6]:


import glob


# In[7]:


glob.glob("../data/sales-*-2014.xlsx")


# This gives us what we need, let's import each of our files and combine them into one file. 
# 
# Panda's concat and append can do this for us. I'm going to use append in this example.
# 
# The code snippet below will initialize a blank DataFrame then append all of the individual files into the all_data DataFrame.

# In[8]:


all_data = pd.DataFrame()
for f in glob.glob("../data/sales-*-2014.xlsx"):
    df = pd.read_excel(f)
    print(df.shape)
    all_data = all_data.append(df,ignore_index=True)


# In[9]:


all_data.shape


# Now we have all the data in our all_data DataFrame. You can use describe to look at it and make sure you data looks good.

# In[10]:


all_data.describe()


# Alot of this data may not make much sense for this data set but I'm most interested in the count row to make sure the number of data elements makes sense.

# In[11]:


all_data.head(16)


# In[11]:


all_data.tail()


# It is not critical in this example but the best practice is to convert the date column to a date time object.

# In[13]:


all_data['date'] = pd.to_datetime(all_data['date'])


# # Combining Data

# Now that we have all of the data into one DataFrame, we can do any manipulations the DataFrame supports. In this case, the next thing we want to do is read in another file that contains the customer status by account. You can think of this as a company's customer segmentation strategy or some other mechanism for identifying their customers.
# 
# First, we read in the data.

# In[14]:


status = pd.read_excel("../data/customer-status.xlsx")
status


# In[15]:


status.shape


# We want to merge this data with our concatenated data set of sales. We use panda's merge function and tell it to do a left join which is similar to Excel's vlookup function.

# In[16]:


all_data_st = pd.merge(all_data, status, how='left')
all_data_st.head(20)


# This looks pretty good but let's look at a specific account.

# In[17]:


all_data_st[all_data_st["account number"]==737550].head()


# This account number was not in our status file, so we have a bunch of NaN's. We can decide how we want to handle this situation. For this specific case, let's label all missing accounts as bronze. Use the fillna function to easily accomplish this on the status column.

# In[20]:


all_data_st['status'].fillna('bronze',inplace=True)
all_data_st


# Check the data just to make sure we're all good.

# In[21]:


all_data_st[all_data_st["account number"]==737550].head()


# Now we have all of the data along with the status column filled in. We can do our normal data manipulations using the full suite of pandas capability.

# # Using Categories

# One of the relatively new functions in pandas is support for categorical data. From the pandas, documentation -
# 
# "Categoricals are a pandas data type, which correspond to categorical variables in statistics: a variable, which can take on only a limited, and usually fixed, number of possible values (categories; levels in R). Examples are gender, social class, blood types, country affiliations, observation time or ratings via Likert scales."
# 
# For our purposes, the status field is a good candidate for a category type.
# 
# You must make sure you have a recent version of pandas installed for this example to work.

# In[22]:


pd.__version__


# First, we typecast it to a category using astype.

# In[24]:


all_data_st["status"] = all_data_st["status"].astype("category")


# This doesn't immediately appear to change anything yet.

# In[25]:


all_data_st.head()


# Buy you can see that it is a new data type.

# In[26]:


all_data_st.dtypes


# Categories get more interesting when you assign order to the categories. Right now, if we call sort on the column, it will sort alphabetically. 

# In[27]:


all_data_st.sort_values(by=["status"]).head()


# We use set_categories to tell it the order we want to use for this category object. In this case, we use the Olympic medal ordering.

# In[28]:


all_data_st["status"].cat.set_categories([ "gold","silver","bronze"],inplace=True)


# Now, we can sort it so that gold shows on top.

# In[29]:


all_data_st.sort_values(by=["status"]).head()


# In[30]:


all_data_st["status"].describe()


# For instance, if you want to take a quick look at how your top tier customers are performaing compared to the bottom. Use groupby to give us the average of the values.

# In[31]:


all_data_st.groupby(["status"])["quantity","unit price","ext price"].mean()


# Of course, you can run multiple aggregation functions on the data to get really useful information 

# In[32]:


all_data_st.groupby(["status"])["quantity","unit price","ext price"].agg([np.sum,np.mean, np.std])


# So, what does this tell you? Well, the data is completely random but my first observation is that we sell more units to our bronze customers than gold. Even when you look at the total dollar value associated with bronze vs. gold, it looks backwards.
# 
# Maybe we should look at how many bronze customers we have and see what is going on.
# 
# What I plan to do is filter out the unique accounts and see how many gold, silver and bronze customers there are.
# 
# I'm purposely stringing a lot of commands together which is not necessarily best practice but does show how powerful pandas can be. Feel free to review my previous articles and play with this command yourself to understand what all these commands mean.

# In[33]:


all_data_st.drop_duplicates(subset=["account number","name"]).iloc[:,[0,1,7]].groupby(["status"])["name"].count()


# Ok. This makes a little more sense. We see that we have 9 bronze customers and only 4 customers. That is probably why the volumes are so skewed towards our bronze customers.

# In[ ]:




