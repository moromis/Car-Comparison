
# coding: utf-8

# # Car Comparison

# ## Gather the data

# In[616]:


# imports
import pandas as pd
import numpy as np
import matplotlib as plt
import re, os, errno, glob


# In[617]:


# get all csv files in the input folder
all_csv_files = glob.glob("input/*.csv")

# create a dataframe for each csv and then concatenate
# into a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_csv_files)
car_data = pd.concat(df_from_each_file, ignore_index=True)


# In[618]:


# let's take a look at our data
car_data.head()


# In[619]:


# we're going to need to clean up the data and turn it into
# numbers (it came in as strings). this is a method to do so
def cleanDataframe(dataframe, column_names, units):
    
    # create a new dataframe
    new_dataframe = dataframe.loc[:]
    for column in column_names:
        
        # keep only digits
        for unit in units:
            new_dataframe[column] = new_dataframe[column].map(lambda x: str(x).strip(unit))
        
        # change nans to -1s
        new_dataframe[column] = new_dataframe[column].map(lambda x: -1 if x == 'nan' else x)
        
        # change the column to a numeric dtype
        new_dataframe[column] = pd.to_numeric(new_dataframe[column])
        
         # change all -1s (nans) to negative max of column (weight poorly) - comment
        # this out if you want to see all results regardless of how spotty
        # the data might be
        # from https://stackoverflow.com/questions/50773107/how-to-replace-infinite-value-with-maximum-value-of-a-pandas-column
        mask = new_dataframe[column] != -1
        new_dataframe.loc[~mask, column] = -float(new_dataframe.loc[mask, column].max())
        
    # return the new, clean dataframe
    return new_dataframe


# In[620]:


# a method to get the top n in a category
def getTopN(dataframe, column_name, n):
    
    # locate the correct column
    column = dataframe[column_name]
    
    # get the n largest entries
    largest = column.nlargest(10)
    
    # get the indices of the rows
    indices = largest.index.values.tolist()
    
    # re-index into the main dataframe
    # and return the results
    return dataframe.iloc[indices]


# ## Clean up the dataset

# In[621]:


def checkNans(dataframe, column_names):
    for column in column_names:
        nans = dataframe[column].isnull().sum()
        total_rows = dataframe.shape[0]
        print('%s out of %s rows in the column \'%s\' are NaNs' % (nans, total_rows, column))


# In[622]:


checkNans(car_data, interesting_columns)


# So only about 250 rows have mpg, and about the same number have max cargo capacity. All listings have fuel tank capacity. How should we deal with NaNs in our data? These are essentially holes in the data. We have two simple options. One is to just make the NaN values 0. In this case they would not really impact our results, and there would be no penalty for lacking data. This would likely make vehicles that are strong in one or two categories and lacking data in the rest rise to the top when they shouldn't necessarily. I'll opt for giving a penalty to data points that are NaN. To do that, I'll take the maximum of each column and insert its negation wherever I see a NaN.

# In[623]:


# the units array is strings that must be removed from the interesting
# columns to isolate the numeric values in the columns. For instance,
# if a value in one of the columns is 'foo 387 gal.', we would need to make sure
# both 'foo' and 'gal.' (note the period) are in the units array
units = ['mpg', 'gal.', 'cu.ft.']
interesting_columns = ['city', 'highway', 'fuel tank capacity', 'max cargo capacity']

# clean up the data
car_data = cleanDataframe(car_data, interesting_columns, units)


# ## Basic Statistics
# We'll run some basic statistics just to see what the best cars in each category are.

# ### What's the top ten cars in terms of cargo space?

# In[624]:


getTopN(car_data, 'max cargo capacity', 10)


# ### What about MPG?

# #### City MPG

# In[625]:


getTopN(car_data, 'city', 10)


# #### Highway MPG

# In[626]:


getTopN(car_data, 'highway', 10)


# ## Largest gas tank?

# In[627]:


getTopN(car_data, 'fuel tank capacity', 10)


# ## Selecting Best Overall

# So that's the raw data. However, we actually need to find the top picks in terms of _all_ these attributes, to the best of our abilities. To do this, we first need to isolate the columns that we're actually interested in

# In[628]:


car_data_subset = car_data[interesting_columns]
car_data_subset.head()


# In[629]:


# we should have no nans
checkNans(car_data_subset, interesting_columns)


# ## Vector Comparison
# Now that we have our subset of data that we're interested in, we can simply compare each row as an n-dimensional vector. Let's try finding our most wanted car using unweighted data, simply finding the magnitude of each vector and keeping the largest vectors we find.

# In[630]:


# first we normalize our data - https://stackoverflow.com/questions/26414913/normalize-columns-of-pandas-data-frame/29651514
from sklearn import preprocessing

values = car_data_subset.values # returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
scaled = min_max_scaler.fit_transform(values)
car_data_subset_norm = pd.DataFrame(scaled)

print(car_data_subset_norm.head())

# now that we've normalized the data, let's find the magnitude of each vector
car_data_magnitudes = car_data_subset_norm.apply(lambda x: np.linalg.norm(np.array(x.tolist())), axis=1)
car_data_magnitudes = pd.DataFrame(car_data_magnitudes)

# change the number in nlargest to how many results you want
largest_magnitudes = car_data_magnitudes.nlargest(100, 0)
indices = largest_magnitudes.index.values.tolist()
best_cars = car_data.iloc[indices]

# Check out the normalized version of the data below:


# In[631]:


# take any negative values (the penalized "data holes") and insert NaNs so they don't show up.
for column in interesting_columns:
    best_cars[column] = best_cars[column].map(lambda x: np.nan if float(x) < 0 else x)
best_cars


# In[632]:


# write the output csv - https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
output_filename = 'output/best_cars_for_me.csv'
if not os.path.exists(os.path.dirname(output_filename)):
    try:
        os.makedirs(os.path.dirname(output_filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

best_cars.to_csv(output_filename)

