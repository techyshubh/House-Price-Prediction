#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import libraries and warnings
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd


# In[2]:


#reading dataset
housing = pd.read_csv('housing.csv')


# In[3]:


#Viewing dataset
housing


# In[4]:


#Checking shape
housing.shape


# In[5]:


#Checking information
housing.info()


# In[6]:


#Checking statistical information
housing.describe()


# ## Step 2: Visualising the Data
# 
# Let's now spend some time doing what is arguably the most important step - **understanding the data**.
# - If there is some obvious multicollinearity going on, this is the first place to catch it
# - Here's where you'll also identify if some predictors directly have a strong association with the outcome variable
# 
# We'll visualise our data using `matplotlib` and `seaborn`.

# In[7]:


import matplotlib.pyplot as plt
import seaborn as sns


# #### Visualising Numeric Variables
# 
# Let's make a pairplot of all the numeric variables

# In[8]:


sns.pairplot(housing)
plt.show()


# #### Visualising Categorical Variables
# 
# As you might have noticed, there are a few categorical variables as well. Let's make a boxplot for some of these variables.

# In[9]:


plt.figure(figsize=(20, 12))
plt.subplot(2,3,1)
sns.boxplot(x = 'mainroad', y = 'price', data = housing)
plt.subplot(2,3,2)
sns.boxplot(x = 'guestroom', y = 'price', data = housing)
plt.subplot(2,3,3)
sns.boxplot(x = 'basement', y = 'price', data = housing)
plt.subplot(2,3,4)
sns.boxplot(x = 'hotwaterheating', y = 'price', data = housing)
plt.subplot(2,3,5)
sns.boxplot(x = 'airconditioning', y = 'price', data = housing)
plt.subplot(2,3,6)
sns.boxplot(x = 'furnishingstatus', y = 'price', data = housing)
plt.show()


# We can also visualise some of these categorical features parallely by using the `hue` argument. Below is the plot for `furnishingstatus` with `airconditioning` as the hue.

# In[10]:


plt.figure(figsize = (10, 5))
sns.boxplot(x = 'furnishingstatus', y = 'price', hue = 'airconditioning', data = housing)
plt.show()


# ## Step 3: Data Preparation

# - You can see that your dataset has many columns with values as 'Yes' or 'No'.
# 
# - But in order to fit a regression line, we would need numerical values and not string. Hence, we need to convert them to 1s and 0s, where 1 is a 'Yes' and 0 is a 'No'.

# In[11]:


# List of variables to map

varlist =  ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']

# Defining the map function
def binary_map(x):
    return x.map({'yes': 1, "no": 0})

# Applying the function to the housing list
housing[varlist] = housing[varlist].apply(binary_map)


# In[12]:


# Check the housing dataframe now

housing.head()


# ### Dummy Variables

# The variable `furnishingstatus` has three levels. We need to convert these levels into integer as well. 
# 
# For this, we will use something called `dummy variables`.

# In[13]:


# Get the dummy variables for the feature 'furnishingstatus' and store it in a new variable - 'status'
status = pd.get_dummies(housing['furnishingstatus'])


# In[14]:


# Check what the dataset 'status' looks like
status.head()


# Now, you don't need three columns. You can drop the `furnished` column, as the type of furnishing can be identified with just the last two columns where — 
# - `00` will correspond to `furnished`
# - `01` will correspond to `unfurnished`
# - `10` will correspond to `semi-furnished`

# In[15]:


# Let's drop the first column from status df using 'drop_first = True'

status = pd.get_dummies(housing['furnishingstatus'], drop_first = True)


# In[16]:


# Add the results to the original housing dataframe

housing = pd.concat([housing, status], axis = 1)


# In[17]:


# Now let's see the head of our dataframe.

housing.head()


# In[18]:


# Drop 'furnishingstatus' as we have created the dummies for it

housing.drop(['furnishingstatus'], axis = 1, inplace = True)


# In[19]:


housing.head()


# ## Step 4: Splitting the Data into Training and Testing Sets
# 
# As you know, the first basic step for regression is performing a train-test split.

# In[20]:


from sklearn.model_selection import train_test_split

# We specify this so that the train and test data set always have the same rows, respectively
np.random.seed(0)
df_train, df_test = train_test_split(housing, train_size = 0.7, test_size = 0.3, random_state = 100)


# ### Rescaling the Features 
# 
# As you saw in the demonstration for Simple Linear Regression, scaling doesn't impact your model. Here we can see that except for `area`, all the columns have small integer values. So it is extremely important to rescale the variables so that they have a comparable scale. If we don't have comparable scales, then some of the coefficients as obtained by fitting the regression model might be very large or very small as compared to the other coefficients. This might become very annoying at the time of model evaluation. So it is advised to use standardization or normalization so that the units of the coefficients obtained are all on the same scale. As you know, there are two common ways of rescaling:
# 
# 1. Min-Max scaling 
# 2. Standardisation (mean-0, sigma-1) 
# 
# This time, we will use MinMax scaling.

# In[21]:


from sklearn.preprocessing import MinMaxScaler


# In[22]:


scaler = MinMaxScaler()


# In[23]:


# Apply scaler() to all the columns except the 'yes-no' and 'dummy' variables
num_vars = ['area', 'bedrooms', 'bathrooms', 'stories', 'parking','price']

df_train[num_vars] = scaler.fit_transform(df_train[num_vars])


# In[24]:


df_train.head()


# In[25]:


df_train.describe()


# In[26]:


# Let's check the correlation coefficients to see which variables are highly correlated

plt.figure(figsize = (16, 10))
sns.heatmap(df_train.corr(), annot = True, cmap="YlGnBu")
plt.show()


# As you might have noticed, `area` seems to the correlated to `price` the most. Let's see a pairplot for `area` vs `price`.

# In[27]:


plt.figure(figsize=[6,6])
plt.scatter(df_train.area, df_train.price)
plt.show()


# So, we pick `area` as the first variable and we'll try to fit a regression line to that.

# ### Dividing into X and Y sets for the model building

# In[28]:


y_train = df_train.pop('price')
X_train = df_train


# ## Step 5: Building a linear model
# 
# Fit a regression line through the training data using `statsmodels`. Remember that in `statsmodels`, you need to explicitly fit a constant using `sm.add_constant(X)` because if we don't perform this step, `statsmodels` fits a regression line passing through the origin, by default.

# In[29]:


import statsmodels.api as sm

# Add a constant
X_train_lm = sm.add_constant(X_train[['area']])

# Create a first fitted model
lr = sm.OLS(y_train, X_train_lm).fit()


# In[30]:


# Check the parameters obtained

lr.params


# In[31]:


# Let's visualise the data with a scatter plot and the fitted regression line
plt.scatter(X_train_lm.iloc[:, 1], y_train)
plt.plot(X_train_lm.iloc[:, 1], 0.127 + 0.462*X_train_lm.iloc[:, 1], 'r')
plt.show()


# In[32]:


# Print a summary of the linear regression model obtained
print(lr.summary())


# ### Adding another variable
# 
# The R-squared value obtained is `0.283`. Since we have so many variables, we can clearly do better than this. So let's go ahead and add the second most highly correlated variable, i.e. `bathrooms`.

# In[33]:


# Assign all the feature variables to X
X_train_lm = X_train[['area', 'bathrooms']]


# In[34]:


# Build a linear model

import statsmodels.api as sm
X_train_lm = sm.add_constant(X_train_lm)

lr = sm.OLS(y_train, X_train_lm).fit()

lr.params


# In[35]:


# Check the summary
print(lr.summary())


# We have clearly improved the model as the value of adjusted R-squared as its value has gone up to `0.477` from `0.281`.
# Let's go ahead and add another variable, `bedrooms`.

# In[36]:


# Assign all the feature variables to X
X_train_lm = X_train[['area', 'bathrooms','bedrooms']]


# In[37]:


# Build a linear model

import statsmodels.api as sm
X_train_lm = sm.add_constant(X_train_lm)

lr = sm.OLS(y_train, X_train_lm).fit()

lr.params


# In[38]:


# Print the summary of the model

print(lr.summary())


# We have improved the adjusted R-squared again. Now let's go ahead and add all the feature variables.

# ### Adding all the variables to the model

# In[39]:


# Check all the columns of the dataframe

housing.columns


# In[40]:


#Build a linear model

import statsmodels.api as sm
X_train_lm = sm.add_constant(X_train)

lr_1 = sm.OLS(y_train, X_train_lm).fit()

lr_1.params


# In[41]:


print(lr_1.summary())


# Looking at the p-values, it looks like some of the variables aren't really significant (in the presence of other variables).
# 
# Maybe we could drop some?
# 
# We could simply drop the variable with the highest, non-significant p value. A better way would be to supplement this with the VIF information. 

# ### Checking VIF
# 
# Variance Inflation Factor or VIF, gives a basic quantitative idea about how much the feature variables are correlated with each other. It is an extremely important parameter to test our linear model. The formula for calculating `VIF` is:
# 
# ### $ VIF_i = \frac{1}{1 - {R_i}^2} $

# In[42]:


# Check for the VIF values of the feature variables. 
from statsmodels.stats.outliers_influence import variance_inflation_factor


# In[43]:


# Create a dataframe that will contain the names of all the feature variables and their respective VIFs
vif = pd.DataFrame()
vif['Features'] = X_train.columns
vif['VIF'] = [variance_inflation_factor(X_train.values, i) for i in range(X_train.shape[1])]
vif['VIF'] = round(vif['VIF'], 2)
vif = vif.sort_values(by = "VIF", ascending = False)
vif


# We generally want a VIF that is less than 5. So there are clearly some variables we need to drop.

# ### Dropping the variable and updating the model
# 
# As you can see from the summary and the VIF dataframe, some variables are still insignificant. One of these variables is, `semi-furnished` as it has a very high p-value of `0.938`. Let's go ahead and drop this variables

# In[44]:


# Dropping highly correlated variables and insignificant variables

X = X_train.drop('semi-furnished', 1,)


# In[45]:


# Build a third fitted model
X_train_lm = sm.add_constant(X)

lr_2 = sm.OLS(y_train, X_train_lm).fit()


# In[46]:


# Print the summary of the model
print(lr_2.summary())


# In[47]:


# Calculate the VIFs again for the new model

vif = pd.DataFrame()
vif['Features'] = X.columns
vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif['VIF'] = round(vif['VIF'], 2)
vif = vif.sort_values(by = "VIF", ascending = False)
vif


# ### Dropping the Variable and Updating the Model
# 
# As you can notice some of the variable have high VIF values as well as high p-values. Such variables are insignificant and should be dropped.
# 
# As you might have noticed, the variable `bedroom` has a significantly high VIF (`6.6`) and a high p-value (`0.206`) as well. Hence, this variable isn't of much use and should be dropped.

# In[48]:


# Dropping highly correlated variables and insignificant variables
X = X.drop('bedrooms', 1)


# In[49]:


# Build a second fitted model
X_train_lm = sm.add_constant(X)

lr_3 = sm.OLS(y_train, X_train_lm).fit()


# In[50]:


# Print the summary of the model

print(lr_3.summary())


# In[51]:


# Calculate the VIFs again for the new model
vif = pd.DataFrame()
vif['Features'] = X.columns
vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif['VIF'] = round(vif['VIF'], 2)
vif = vif.sort_values(by = "VIF", ascending = False)
vif


# ### Dropping the variable and updating the model

# As you might have noticed, dropping `semi-furnised` decreased the VIF of `mainroad` as well such that it is now under 5. But from the summary, we can still see some of them have a high p-value. `basement` for instance, has a p-value of 0.03. We should drop this variable as well.

# In[52]:


X = X.drop('basement', 1)


# In[53]:


# Build a fourth fitted model
X_train_lm = sm.add_constant(X)

lr_4 = sm.OLS(y_train, X_train_lm).fit()


# In[54]:


print(lr_4.summary())


# In[55]:


# Calculate the VIFs again for the new model
vif = pd.DataFrame()
vif['Features'] = X.columns
vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif['VIF'] = round(vif['VIF'], 2)
vif = vif.sort_values(by = "VIF", ascending = False)
vif


# Now as you can see, the VIFs and p-values both are within an acceptable range. So we go ahead and make our predictions using this model only.

# ## Step 7: Residual Analysis of the train data
# 
# So, now to check if the error terms are also normally distributed (which is infact, one of the major assumptions of linear regression), let us plot the histogram of the error terms and see what it looks like.

# In[56]:


y_train_price = lr_4.predict(X_train_lm)


# In[57]:


# Plot the histogram of the error terms
fig = plt.figure()
sns.distplot((y_train - y_train_price), bins = 20)
fig.suptitle('Error Terms', fontsize = 20)                  # Plot heading 
plt.xlabel('Errors', fontsize = 18)                         # X-label


# ## Step 8: Making Predictions Using the Final Model
# 
# Now that we have fitted the model and checked the normality of error terms, it's time to go ahead and make predictions using the final, i.e. fourth model.

# #### Applying the scaling on the test sets

# In[58]:


num_vars = ['area', 'bedrooms', 'bathrooms', 'stories', 'parking','price']

df_test[num_vars] = scaler.transform(df_test[num_vars])


# In[59]:


df_test.describe()


# #### Dividing into X_test and y_test

# In[60]:


y_test = df_test.pop('price')
X_test = df_test


# In[61]:


# Adding constant variable to test dataframe
X_test_m4 = sm.add_constant(X_test)


# In[62]:


# Creating X_test_m4 dataframe by dropping variables from X_test_m4

X_test_m4 = X_test_m4.drop(["bedrooms", "semi-furnished", "basement"], axis = 1)


# In[63]:


# Making predictions using the fourth model

y_pred_m4 = lr_4.predict(X_test_m4)


# ## Step 9: Model Evaluation
# 
# Let's now plot the graph for actual versus predicted values.

# In[64]:


# Plotting y_test and y_pred to understand the spread

fig = plt.figure()
plt.scatter(y_test, y_pred_m4)
fig.suptitle('y_test vs y_pred', fontsize = 20)              # Plot heading 
plt.xlabel('y_test', fontsize = 18)                          # X-label
plt.ylabel('y_pred', fontsize = 16)      


# 
# We can see that the equation of our best fitted line is:
# 
# $ price = 0.236  \times  area + 0.202  \times  bathrooms + 0.11 \times stories + 0.05 \times mainroad + 0.04 \times guestroom + 0.0876 \times hotwaterheating + 0.0682 \times airconditioning + 0.0629 \times parking + 0.0637 \times prefarea - 0.0337 \times unfurnished $

# Overall we have a decent model, but we also acknowledge that we could do better. 
# 
# We have a couple of options:
# 1. Add new features (bathrooms/bedrooms, area/stories, etc.)
# 2. Build a non-linear model

# In[65]:


from sklearn.metrics import r2_score


# In[66]:


r2_score(y_test, y_pred_m4)


# ## Using Decision Tree

# In[67]:


from sklearn.tree import DecisionTreeRegressor


# In[68]:


dt = DecisionTreeRegressor(random_state=42, max_depth=4, min_samples_leaf=10)


# In[69]:


np.random.seed(0)
df_train, df_test = train_test_split(housing, random_state=100, train_size=0.7)


# In[70]:


df_train.shape, df_test.shape


# In[71]:


df_test.head()


# In[72]:


scaler = MinMaxScaler()


# In[73]:


df_train['price']= scaler.fit_transform(df_train[['price']])
df_test['price']= scaler.transform(df_test[['price']])


# In[74]:


df_train['price'].describe()


# In[75]:


y_train = df_train.pop('price')
X_train = df_train

y_test = df_test.pop('price')
X_test = df_test


# In[76]:


X_train.shape, X_test.shape


# ### Fit the dt Model

# In[77]:


dt.fit(X_train, y_train)


# In[78]:


from IPython.display import Image
from six import StringIO
from sklearn.tree import export_graphviz
import pydotplus, graphviz

dot_data = StringIO()
export_graphviz(dt, out_file= dot_data, filled = True, rounded = True,
               feature_names = X_train.columns)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(graph.create_png())


# In[81]:


y_train_pred = dt.predict(X_train)


# In[82]:


r2_score(y_train, y_train_pred)


# In[83]:


y_test_pred = dt.predict(X_test)


# In[84]:


r2_score(y_test, y_test_pred)


# ## Using Random Forest Regressor

# In[85]:


from sklearn.ensemble import RandomForestRegressor


# In[86]:


rf = RandomForestRegressor(random_state=42, min_samples_leaf=10, n_jobs=-1, max_depth =5)


# In[87]:


rf.fit(X_train, y_train)


# In[88]:


sample_tree = rf.estimators_[20]


# In[89]:


dot_data = StringIO()
export_graphviz(sample_tree, out_file= dot_data, filled = True, rounded = True,
               feature_names = X_train.columns)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
Image(graph.create_png())


# In[90]:


y_train_pred = rf.predict(X_train)
y_test_pred= rf.predict(X_test)


# In[91]:


r2_score(y_train, y_train_pred)


# In[92]:


r2_score(y_test, y_test_pred)


# In[93]:


rf.feature_importances_


# In[94]:


imp_df= pd.DataFrame({ 'Varibale_Name': X_train.columns,
         'Feature_importance': rf.feature_importances_
})


# In[95]:


imp_df.nlargest(10, 'Feature_importance')


# In[96]:


imp_df.sort_values(by= "Feature_importance", ascending=False)

