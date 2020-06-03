# Importing necessary packages
import pandas as pd
import numpy as np
import datetime
import geocoder
from geopy.geocoders import Nominatim
from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather

# Reading monthly yellow taxi trip data for 2019
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

# Dropping rows with N/A's in each month
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

# Concatenating monthly data and removing unnecessary columns
data = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12])
data.drop(['VendorID', 'store_and_fwd_flag', 'congestion_surcharge', 'RatecodeID', 'payment_type', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'congestion_surcharge'], axis = 1, inplace = True)

# Removing insensible data
data = data.loc[(data.passenger_count > 0),:] # Passenger count cannot be less than or equal zero 
data = data.loc[(data.trip_distance > 0),:] # Trip Distance should be greater than zero
data = data.loc[(data.total_amount > 2.5),:] # Minimum Yellow Taxi fare in NYC is $2.50
data = data[data.total_amount < 75] # Removing outliers 
data = data[data.trip_distance < 40] # Removing outliers

# Removing entries other than 2019
data['Pyear'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).year
data['Dyear'] = pd.DatetimeIndex(data['tpep_dropoff_datetime']).year
data = data.loc[(data.Pyear == 2019),:]
data = data.loc[(data.Dyear == 2019),:]

# Calculating Duration from Pickup and Dropoff Timestamp
data['tpep_pickup_datetime'] = pd.to_datetime(data.tpep_pickup_datetime)
data['tpep_dropoff_datetime'] = pd.to_datetime(data.tpep_dropoff_datetime)
data['Duration'] = data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime']
data['Duration'] = data.Duration.dt.total_seconds()/60
data['Duration'] = round(data['Duration'])
data = data[data.Duration > 0]
data = data[data.Duration < 180]

# Feature Extraction
data['Month'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).month
data['Day'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).day_name()
data['Hour'] = pd.DatetimeIndex(data['tpep_pickup_datetime']).hour
data['tpep_pickup_datetime'] = data['tpep_pickup_datetime'].apply(str)
data['tpep_pickup_datetime'] = data.tpep_pickup_datetime.map(lambda x:str(x)[:13])
data['tpep_pickup_datetime'] = pd.to_datetime(data.tpep_pickup_datetime)
data.reset_index(inplace = True)
data.drop(['tpep_dropoff_datetime', 'DOLocationID', 'Pyear', 'Dyear', 'index'] , axis = 1, inplace = True)

# Finding top 20 pickup location zones based on total number of trips recorded
loc_cnt = pd.DataFrame(data['PULocationID'].value_counts())
loc_cnt['StationID'] = loc_cnt.index
loc_cnt.rename(columns={'PULocationID':'Count'}, inplace=True)
loc_cnt = loc_cnt[['StationID', 'Count']]
loc_cnt.reset_index(inplace = True)
loc_cnt.drop('index', axis = 1, inplace = True)
stations = list(loc_cnt.head(20)['StationID'])

# Removing records happened in zones other than the top 20 zones
data = data[data.PULocationID.isin(stations)]
data.reset_index(inplace = True)
data.drop('index', axis = 1, inplace = True)

# Renaming columns accordingly 
data.rename(columns={'PULocationID':'LocationID', 'tpep_pickup_datetime': 'Pickuptime', 'passenger_count': 'Passengercount', 'trip_distance': 'Tripdistance', 'total_amount': 'Amount'}, inplace=True)
data = data[['LocationID', 'Pickuptime', 'Month', 'Day', 'Hour', 'Duration', 'Passengercount', 'Tripdistance', 'Amount']]

# Grouping dataframe with respect to Location ID, Pickup time, Month, Day, Hour to find hourly demand
counts = pd.DataFrame(data.groupby(['LocationID', 'Pickuptime', 'Month', 'Day', 'Hour']).agg({'Pickuptime': 'count', 'Duration': 'mean', 'Passengercount': 'mean', 'Tripdistance': 'mean', 'Amount': 'mean'}))
counts.rename(columns={'Pickuptime':'Demand'}, inplace=True)
counts.reset_index(inplace = True)
counts = counts.round(2)
counts.to_csv('counts.csv', index=False)

# Extracting Latitudes and Longitudes for the corresponding pickup zones
location = pd.read_csv('taxi+_zone_lookup.csv')
locs = list(counts['LocationID'].unique())
location = location[location.LocationID.isin(locs)]
location.reset_index(inplace = True)
location.drop(['index', 'service_zone'], axis = 1, inplace = True)
geolocator = Nominatim(user_agent="map")
lat = []
long = []
for ele in location['Zone']:
    loca = geolocator.geocode(ele + ' NYC')
    lat.append(loca.latitude)
    long.append(loca.longitude)
location['Latitude'] = lat
location['Longitude'] = long
location.to_csv('Locations.csv', index = False)
df = pd.merge(counts, location, on='LocationID')
df.to_csv('Merged.csv', index = False)

# Extracting daily weather data for Manhattan and Queens from DarkSky API for the year 2019
API_KEY = 'Your Key'
darksky = DarkSky(API_KEY)
dates = df['Pickuptime'].dt.date.unique()
temp_man = pd.DataFrame(columns = ['Date', 'Hour', 'Temperature', 'Windspeed', 'Windgust', 'Windbearing', 'Visibility'])
temp_que = pd.DataFrame(columns = ['Date', 'Hour', 'Temperature', 'Windspeed', 'Windgust', 'Windbearing', 'Visibility'])
man_lat = 40.75688
man_long = -73.9828
que_lat = 40.6433
que_long = -73.7889
# Manhattan Weather Data
for i in range(len(dates)):
    forecast = darksky.get_time_machine_forecast(man_lat, man_long, pd.to_datetime(dates[i]))
    for j in range(len(forecast.hourly.data)):
        temp = forecast.hourly.data[j].temperature
        ws = forecast.hourly.data[j].wind_speed
        wg = forecast.hourly.data[j].wind_gust
        wb = forecast.hourly.data[j].wind_bearing
        vs = forecast.hourly.data[j].visibility
        newrow = {'Date': str(dates[i]), 'Hour': j, 'Temperature': temp, 'Windspeed': ws, 'Windgust': wg, 'Windbearing': wb, 'Visibility': vs}
        temp_man = temp_man.append(newrow, ignore_index = True)
# Queens Weather Data
for i in range(len(dates)):
    forecast = darksky.get_time_machine_forecast(que_lat, que_long, pd.to_datetime(dates[i]))
    for j in range(len(forecast.hourly.data)):
        temp = forecast.hourly.data[j].temperature
        ws = forecast.hourly.data[j].wind_speed
        wg = forecast.hourly.data[j].wind_gust
        wb = forecast.hourly.data[j].wind_bearing
        vs = forecast.hourly.data[j].visibility
        newrow = {'Date': str(dates[i]), 'Hour': j, 'Temperature': temp, 'Windspeed': ws, 'Windgust': wg, 'Windbearing': wb, 'Visibility': vs}
        temp_que = temp_que.append(newrow, ignore_index = True)
temp_man['Borough'] = "Manhattan"
temp_que['Borough'] = "Queens"
temperature = pd.concat([temp_man, temp_que], ignore_index = True)
temperature.to_csv('Temperature.csv', index = False)

# Merging the dataframe with the weather data
df['Date'] = pd.DatetimeIndex(df['Pickuptime']).date
temperature['Date'] = pd.DatetimeIndex(temperature['Date']).date
final = pd.merge(df, temperature, on=['Borough', 'Date', 'Hour'], how = 'left')
final.rename(columns={'Temperature':'Temperature(F)', 'Duration': 'Duration(mins)', 'Tripdistance': 'Tripdistance(Miles)', 'Amount': 'Amount($)', 'Windspeed': 'Windspeed(MPH)', 'Windgust': 'Windgust(MPH)', 'Visibility': 'Visibility(Miles)'}, inplace=True)
final.drop(['Pickuptime', 'Borough', 'Zone', 'Latitude', 'Longitude', 'Date'] , axis = 1, inplace = True)

# Final CSV for Modeling 
final.to_csv('Model.csv', index = False)
