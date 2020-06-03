import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt



df1 = pd.read_csv("yellow_tripdata_2019-01.csv", low_memory = False)
df2 = pd.read_csv("yellow_tripdata_2019-02.csv", low_memory = False)
df3 = pd.read_csv("yellow_tripdata_2019-03.csv", low_memory = False)
df4 = pd.read_csv("yellow_tripdata_2019-04.csv", low_memory = False)
df5 = pd.read_csv("yellow_tripdata_2019-05.csv", low_memory = False)
df6 = pd.read_csv("yellow_tripdata_2019-06.csv", low_memory = False)
df7 = pd.read_csv("yellow_tripdata_2019-07.csv", low_memory = False)
df8 = pd.read_csv("yellow_tripdata_2019-08.csv", low_memory = False)
df9 = pd.read_csv("yellow_tripdata_2019-09.csv", low_memory = False)
df10 = pd.read_csv("yellow_tripdata_2019-10.csv", low_memory = False)
df11 = pd.read_csv("yellow_tripdata_2019-11.csv", low_memory = False)
df12 = pd.read_csv("yellow_tripdata_2019-12.csv", low_memory = False)

df1.dropna(inplace = True)
df2.dropna(inplace = True)
df3.dropna(inplace = True)
df4.dropna(inplace = True)
df5.dropna(inplace = True)
df6.dropna(inplace = True)
df7.dropna(inplace = True)
df8.dropna(inplace = True)
df9.dropna(inplace = True)
df10.dropna(inplace = True)
df11.dropna(inplace = True)
df12.dropna(inplace = True)

data = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12])
data.drop(['VendorID', 'store_and_fwd_flag', 'congestion_surcharge', 'RatecodeID', 'payment_type', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'congestion_surcharge'], axis = 1, inplace = True)

data = data.loc[(data.passenger_count > 0),: ]
data = data.loc[(data.trip_distance > 1),:]
data = data.loc[(data.total_amount > 3.5),:]

data['Pyear'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).year
data['Dyear'] = pd.DatetimeIndex(data['tpep_dropoff_datetime']).year

data = data.loc[(data.Pyear == 2019),: ]
data = data.loc[(data.Dyear == 2019),: ]
data['tpep_pickup_datetime'] = pd.to_datetime(data.tpep_pickup_datetime)
data['tpep_dropoff_datetime'] = pd.to_datetime(data.tpep_dropoff_datetime)
data['Duration'] = data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime']
data['Duration'] = data.Duration.dt.total_seconds()/60
data['Duration'] = round(data['Duration'])
data = data[data.Duration > 0]
data = data[data.Duration < 180]
data = data[data.total_amount < 75]
data = data[data.trip_distance < 40]

data['Month'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).month
data['Day'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).day_name()
data['Hour'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).hour
data['tpep_pickup_datetime'] = data['tpep_pickup_datetime'].apply(str)
data['tpep_pickup_datetime'] = data.tpep_pickup_datetime.map(lambda x:str(x)[:13])
data['tpep_pickup_datetime'] = pd.to_datetime(data.tpep_pickup_datetime)
data.reset_index(inplace = True)
data.drop(['tpep_dropoff_datetime', 'DOLocationID', 'Pyear', 'Dyear', 'index'] , axis = 1, inplace = True)

loc_cnt = pd.DataFrame(data['PULocationID'].value_counts())
loc_cnt['StationID'] = loc_cnt.index
loc_cnt.rename(columns={'PULocationID':'Count'}, inplace=True)
loc_cnt = loc_cnt[['StationID', 'Count']]
loc_cnt.reset_index(inplace = True)
loc_cnt.drop('index', axis = 1, inplace = True)

stations = list(loc_cnt.head(20)['StationID'])

data = data[data.PULocationID.isin(stations)]
data.reset_index(inplace = True)
data.drop('index', axis = 1, inplace = True)

data.rename(columns={'PULocationID':'LocationID', 'tpep_pickup_datetime': 'Pickuptime', 'passenger_count': 'Passengercount', 'trip_distance': 'Tripdistance', 'total_amount': 'Amount'}, inplace=True)
data = data[['LocationID', 'Pickuptime', 'Month', 'Day', 'Hour', 'Duration', 'Passengercount', 'Tripdistance', 'Amount']]

counts = pd.DataFrame(data.groupby(['LocationID', 'Pickuptime', 'Month', 'Day', 'Hour']).agg({'Pickuptime': 'count', 'Duration': 'mean', 'Passengercount': 'mean', 'Tripdistance': 'mean', 'Amount': 'mean'}))
counts.rename(columns={'Pickuptime':'Demand'}, inplace=True)
counts.reset_index(inplace = True)
counts = counts.round(2)
counts.to_csv('counts.csv', index=False)

location = pd.read_csv('Locations.csv')
df = pd.merge(counts, location, on='LocationID')
t = pd.to_datetime('2019-03-11 23')
df = df[df.Pickuptime != t]
df.to_csv('Merged.csv', index = False)


temperature = pd.read_csv('Temperature.csv')

df['Date'] = pd.DatetimeIndex(df['Pickuptime']).date
temperature['Date'] = pd.DatetimeIndex(temperature['Date']).date

final = pd.merge(df, temperature, on=['Borough', 'Date', 'Hour'], how = 'left')
final.rename(columns={'Temperature':'Temperature(F)', 'Duration': 'Duration(mins)', 'Tripdistance': 'Tripdistance(Miles)', 'Amount': 'Amount($)', 'Windspeed': 'Windspeed(MPH)', 'Windgust': 'Windgust(MPH)', 'Visibility': 'Visibility(Miles)'}, inplace=True)
final.to_csv('final_2.csv', index = False)


final.drop(['Pickuptime', 'Borough', 'Zone', 'Latitude', 'Longitude', 'Date'] , axis = 1, inplace = True)
final.to_csv('Model.csv', index = False)


















