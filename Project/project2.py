

!apt-get update # Update apt-get repository.
!apt-get install openjdk-8-jdk-headless -qq > /dev/null # Install Java.
!wget -q http://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz # Download Apache Sparks.
!tar xf spark-3.1.1-bin-hadoop3.2.tgz # Unzip the tgz file.
!pip install -q findspark # Install findspark.

# Set environment variables
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.1-bin-hadoop3.2"

# Initialize findspark
import findspark
findspark.init()

# Create a PySpark session
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()
from pyspark.sql import functions as F
spark

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.offline as pyo
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot
import seaborn as sns
import numpy as np



# holt winters
# single exponential smoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
# double and triple exponential smoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from itertools import product


from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error

from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf, PandasUDFType, col
from pyspark.sql.types import *

df = pd.read_csv('train.csv')

df.head(10)

df.tail(10)

print('column name'.ljust(20), '# unique values')
for col in df[['store','item']]:
    print(col.ljust(20), '=>', len(df[col].unique()))

print(df['store'].unique())

print(df['item'].unique())

df.info()

df.isna().sum()

df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')



# Data Visualization

plt.hist(df['sales'], color = 'blue', edgecolor = 'black',
         bins = int(180/5))


plt.title('Histogram of sales')
plt.xlabel('sales')
plt.ylabel('sales frequency')

import plotly.offline as pyo
pyo.init_notebook_mode()
daily_sales = df.groupby('date', as_index=False)['sales'].sum()
store_daily_sales = df.groupby(['store', 'date'], as_index=False)['sales'].sum()
item_daily_sales = df.groupby(['item', 'date'], as_index=False)['sales'].sum()

daily_sales_sc = go.Scatter(x=daily_sales['date'], y=daily_sales['sales'])
layout = go.Layout(title='Daily sales', xaxis=dict(title='Date'), yaxis=dict(title='Sales'))
fig = go.Figure(data=[daily_sales_sc], layout=layout)
fig.show(renderer="colab")
iplot(fig)

store_daily_sales_sc = []
for store in store_daily_sales['store'].unique():
    current_store_daily_sales = store_daily_sales[(store_daily_sales['store'] == store)]
    store_daily_sales_sc.append(go.Scatter(x=current_store_daily_sales['date'], y=current_store_daily_sales['sales'], name=('Store %s' % store)))

layout = go.Layout(title='Store daily sales', xaxis=dict(title='Date'), yaxis=dict(title='Sales'))
fig = go.Figure(data=store_daily_sales_sc, layout=layout)
fig.show(renderer="colab")
iplot(fig)

item_daily_sales_sc = []
for item in item_daily_sales['item'].unique():
    current_item_daily_sales = item_daily_sales[(item_daily_sales['item'] == item)]
    item_daily_sales_sc.append(go.Scatter(x=current_item_daily_sales['date'], y=current_item_daily_sales['sales'], name=('Item %s' % item)))

layout = go.Layout(title='Item daily sales', xaxis=dict(title='Date'), yaxis=dict(title='Sales'))
fig = go.Figure(data=item_daily_sales_sc, layout=layout)
fig.show(renderer="colab")
iplot(fig)

item_sales = df.groupby('item')['sales'].sum()

# Sort by sales in descending order
sorted_item_sales = item_sales.sort_values(ascending=False)

# Select top 5 items
top_5_items = sorted_item_sales.head(5)

top_5_items

top_5_data = df[df['item'].isin(top_5_items.index)]

top_5_data['item'].unique()

item_5_daily_sales_bar = []

for item in top_5_data['item'].unique():
    current_item_daily_sales = top_5_data[(top_5_data['item'] == item)]
    item_5_daily_sales_bar.append(go.Scatter(x=current_item_daily_sales['date'], y=current_item_daily_sales['sales'], name=('Item %s' % item)))

layout = go.Layout(title='Item daily sales for top 5 items', xaxis=dict(title='Date'), yaxis=dict(title='Sales'))
fig = go.Figure(data=item_5_daily_sales_bar, layout=layout)
fig.show(renderer="colab")
iplot(fig)

grouped = top_5_data.groupby('item')['sales'].sum()
item_sales_bar = top_5_data.groupby('item')['sales'].sum().reset_index()

item_sales_bar

top_items_bar = item_sales_bar.nlargest(5, 'sales')

top_items_bar

top_items_bar["item"]=top_items_bar["item"].astype(str)

import plotly.express as px

fig = px.bar(top_items_bar, x='item', y='sales',
            color='item',
             labels={''}, height=400)
fig.update_layout(showlegend=False)
fig.show(renderer="colab")

fig.show()

store_daily_sales = df.groupby(['store'], as_index=False)['sales'].sum().sort_values('sales')

store_daily_sales["store"]=store_daily_sales["store"].astype(str)

fig = px.bar(store_daily_sales, x='store', y='sales',
            color='store',
             labels={'pop':'population of Canada'}, height=400)

fig.update_layout(showlegend=False)
fig.show(renderer="colab")

fig.show()

# Date features

df_date=df.copy()

df_date.dtypes

from datetime import date

df_date['year'] = df_date['date'].dt.isocalendar().year
df_date['month'] = df_date['date'].dt.month
df_date['day'] = df_date['date'].dt.day
df_date['weekofyear'] = df_date['date'].dt.isocalendar().week
df_date['dayofweek'] = df_date['date'].dt.dayofweek

df_date

month_sales = df_date.groupby(['month'], as_index=False)['sales'].sum().sort_values('sales')

month_sales["month"]=month_sales["month"].astype(int)

month_sales

fig = px.bar(month_sales, x='month', y='sales',
            color='month',
              height=400)

fig.update_xaxes(dtick="M1", tickformat="%Y-%m")
fig.update_layout(showlegend=False)
fig.show(renderer="colab")
fig.show()

df_date['day'].unique()

day_sales = df_date.groupby(['day'], as_index=False)['sales'].sum().sort_values('sales')

day_sales["day"]=day_sales["day"].astype(int)

fig = px.bar(day_sales, x='day', y='sales',
            color='day',
              height=400)

fig.update_xaxes(dtick="M1", tickformat="%Y-%m")
fig.update_layout(showlegend=False)
fig.show(renderer="colab")
fig.show()

week_day_sales = df_date.groupby(['dayofweek'], as_index=False)['sales'].sum().sort_values('sales')

week_day_sales["dayofweek"]=week_day_sales["dayofweek"].astype(int)

fig = px.bar(week_day_sales, x='dayofweek', y='sales',
            color='dayofweek',
              height=400)

fig.update_xaxes(dtick="M1", tickformat="%Y-%m")
fig.update_layout(showlegend=False)
fig.show(renderer="colab")

fig.show()

week_year_sales = df_date.groupby(['weekofyear'], as_index=False)['sales'].sum().sort_values('sales')
week_year_sales["weekofyear"]=week_year_sales["weekofyear"].astype(int)
fig = px.bar(week_year_sales, x='weekofyear', y='sales',
            color='weekofyear',
              height=400)

fig.update_xaxes(dtick="M1", tickformat="%Y-%m")
fig.update_layout(showlegend=False)
fig.show(renderer="colab")
fig.show()

plt.figure(figsize=(12*2,6))

ax=sns.boxplot(data=df, x='store', y='sales', hue='store')

# Set labels and title
plt.xlabel('Store')
plt.ylabel('Sales')
plt.title('Outlier Box Plot of Sales for Each Store-Item Combination')

# Show the plot

ax.get_legend().remove()

plt.show()

s = pd.Series([1,2,3,4,5,6,7,8,9,10])
print(s.describe(percentiles=[.75]))

x=s.describe(percentiles=[.75]).T.reset_index()

x.T

df_out=df.copy()



df_describe=df_out[['store','sales']].groupby(['store']).apply(lambda g : g['sales'].describe(percentiles = [.75]).T).reset_index()

df_out=df_out.merge(df_describe[['store','mean','75%']], on=['store'], how='left')

df_out

df_out['sales_imputed'] = np.where(df_out["sales"] >= df_out["75%"], df_out["mean"], df_out["sales"])

df_out = df_out[['date', 'store', 'item', 'sales_imputed']]
df_out.rename(columns = {'sales_imputed':'sales'}, inplace = True)

df_out





# example

df_store_1=df[df['store']==1]

df_store_1['sales'].describe()

df_describe.columns

df_date

print(df_date[df['store']==1].head())

## Modelling

import datetime

schema_df = StructType([

                     StructField('date', TimestampType()),
                     StructField('item', StringType()),
                     StructField('sales', DoubleType()),
                     StructField('predictions', DoubleType())
])

@pandas_udf(schema_df, PandasUDFType.GROUPED_MAP)
def holts(df):

    print(df)
    edf = df[['date','sales']]
    edf['date'] = pd.to_datetime(edf['date'])


    split_date = pd.to_datetime('2017-11-30')

    train_set=edf.loc[edf['date'] <= split_date]
    test_set = edf.loc[edf['date'] > split_date]


    train_set.set_index('date',inplace=True)
    test_set.set_index('date',inplace=True)

    train_set=train_set['sales'].resample('D').mean()

    train_set.asfreq("D")

    test_set=test_set['sales'].resample('D').mean()

    test_set.asfreq("D")

    hw_model1 = ExponentialSmoothing(train_set, trend="additive", seasonal="additive", seasonal_periods=365)
    fit2 = hw_model1.fit(optimized=True)
    #predicting it on train series (ts)
    pred_ts_t_HW = fit2.predict(start=test_set.index[0], end = test_set.index[-1])


    predictions_hw_df = pred_ts_t_HW.reset_index().rename(columns={'index': 'date', 'pred_ts_t_HW': 'prediction'})
    predictions_hw_df=predictions_hw_df.rename(columns={0: "predictions"})


    predictions_hw_df=predictions_hw_df.merge(test_set, on='date', how='left')
    predictions_hw_df['item'] = df['item'].iloc[0]
    predictions_hw_df['item'] = predictions_hw_df['item'].apply(str)

    # predictions_hw_df=predictions_hw_df.merge(test_set, on='date', how='left')
    # predictions_hw_df['store'] = df['store'].iloc[0]

    # predictions_hw_df['store'] = predictions_hw_df['store'].apply(str)



    # date # store # test # predicted



    return predictions_hw_df

df_spark = spark.read.options(header='True', inferSchema='True').csv(f'train.csv')
df_spark = df_spark.select(F.col("date"), F.col('item'), F.col("sales"))

df[['col','col2']]

df_spark.schema.names

df_spark.printSchema()

results_df = df_spark.groupby(['item']).apply(holts)

results_df.show()

results_df.printSchema()

start = time.time()
results_df.show()
end = time.time()
print("The time of execution of above program is :",
      (end-start))



from pyspark.sql.functions import date_format

results_df = results_df.withColumn("date", date_format("date", "yyyy-MM-dd HH:mm:ss")).toPandas()

results_df['item'].unique()

results_df

print(mean_absolute_percentage_error(results_df['sales'],results_df['predictions']))

print(mean_absolute_error(results_df['sales'],results_df['predictions']))

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#

# Trying with group by from pandas

def holts_pandas(df):

    edf = df[['date','sales']]
    edf['date'] = pd.to_datetime(edf['date'])


    split_date = pd.to_datetime('2017-11-30')

    train_set=edf.loc[edf['date'] <= split_date]
    test_set = edf.loc[edf['date'] > split_date]


    train_set.set_index('date',inplace=True)
    test_set.set_index('date',inplace=True)

    train_set=train_set['sales'].resample('D').mean()

    train_set.asfreq("D")

    test_set=test_set['sales'].resample('D').mean()

    test_set.asfreq("D")

    hw_model1 = ExponentialSmoothing(train_set, trend="additive", seasonal="additive", seasonal_periods=365)
    fit2 = hw_model1.fit(optimized=True)
    #predicting it on train series (ts)
    pred_ts_t_HW = fit2.predict(start=test_set.index[0], end = test_set.index[-1])


    predictions_hw_df = pred_ts_t_HW.reset_index().rename(columns={'index': 'date', 'pred_ts_t_HW': 'prediction'})
    predictions_hw_df=predictions_hw_df.rename(columns={0: "predictions"})


    predictions_hw_df=predictions_hw_df.merge(test_set, on='date', how='left')
    predictions_hw_df['item'] = df['item'].iloc[0]
    predictions_hw_df['item'] = predictions_hw_df['item'].apply(str)

    # predictions_hw_df=predictions_hw_df.merge(test_set, on='date', how='left')
    # predictions_hw_df['store'] = df['store'].iloc[0]

    # predictions_hw_df['store'] = predictions_hw_df['store'].apply(str)

    # date # store # test # predicted



    return predictions_hw_df

df_pandas = pd.read_csv(f'train.csv')
df_pandas = df_pandas[['date','item','sales']]

import time
start = time.time()

results_pandas = df_pandas.groupby(['item']).apply(holts_pandas)

end = time.time()

print("The time of execution of above program is :",
      (end-start) )

time_spark=3.6809322834014893
time_pd=78.33949851989746

percent_diff=((time_pd-time_spark)/(time_pd)*100)
print("Percentage diff: {0} %\n".format(round(percent_diff)))

###################################################################

import datetime

split_date = pd.to_datetime('2017-11-30')
split_date

pd.to_datetime(df_date['date'].max())

train_set=df_date.loc[df_date['date'] <= split_date]
test_set = df_date.loc[df_date['date'] > split_date]


# train_data = train_data.loc[train_data['Date'] <= split_date]
# validation_data = train_data.loc[train_data['Date'] > split_date]

df_date.dtypes





train_set.set_index('date',inplace=True)

train_set['store'].unique()

test_set.set_index('date',inplace=True)

train_set=train_set['sales'].resample('D').mean()

test_set=test_set['sales'].resample('D').mean()

train_set.asfreq("D")

test_set.asfreq("D")

print(train_set.index.freq)

print(test_set.index.freq)

len(test_set)

hw_model1 = ExponentialSmoothing(train_set, trend="additive", seasonal="additive", seasonal_periods=365)
fit2 = hw_model1.fit(optimized=True)
#predicting it on train series (ts)
pred_ts_t_HW = fit2.predict(start=test_set.index[0], end = test_set.index[-1])

predictions_hw_df = pred_ts_t_HW.reset_index().rename(columns={'index': 'date', 'pred_ts_t_HW': 'prediction'})

predictions_hw_df

predictions_hw_df=predictions_hw_df.rename(columns={0: "predictions"})

predictions_hw_df

test_set

len(test_set)

predictions_hw_df=predictions_hw_df.merge(test_set, on='date', how='left')

predictions_hw_df

len(predictions_hw_df)

predictions_hw_df['store'] = df_date['store'].iloc[0]

predictions_hw_df

value = df_date.iloc[0]['store']

value

