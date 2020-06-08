
# Visualization of New York City Yellow Taxi Trip Data (2019)

---

## Introduction
*The fast-paced and connected world is run by many services and the subtle but vital one is taxi services. The yellow taxi is the heartbeat of economic capital (New York City) and being a part of its culture gives us enough reason to analyse them deeply. The Yellow Taxicab Co. was incorporated in New York on April 4, 1912. Yellow taxi in New York city had roughly around 14000 cabs permitted to operate in the city as per 2014. The taxi takes people from one location to other location within NYC and its demand is influenced by many factors like duration, trip distance, number of passengers, pickup locations, etc. The factors discussed above, and other uncertain factors has become a very important aspect to be discussed and visualized upon. Also, considering external atmospheric conditions as an important factor could lead us to a better predictive model. As a result, it becomes essential to analyse underlying factors and subtle parameters to enhance the existing system to have a better overview on the demand of taxis.*

---

## Sources
- [NYC Yellow Taxi Data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- The weather data from [DarkSky API](https://darksky.net/dev)
---

## Packages used for EDA
```
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets.embed import embed_minimal_html
```
- *Note:The following packages need to be installed:* 
- *pip install seaborn*
- *pip install ipywidgets.embed*

### Data Visualization:
#### Visualization of prominent Contributing Factors using Stacked Bar and Pie Chart
*Exploratory Data Analysis is a process of conducting initial investigations on data set to identify patterns, anomalies, to test hypothesis and to check assumptions with the help of summary statistics and graphical representations. Before removing the outliers from the dataset the distribution of predictors are highly skewed which is evident from Fig. 3.4.1. After removing outliers, the distribution of parameters turns out to be normalized (Fig. 3.4.2). Making the predictor more normalized gives us the better model.*
*The insights that can be derived from the Scatter Matrix Plot are:*
- *Most of the trips recorded had the passenger count to be in two’s and three’s, this shows that most of the passengers who opted for the yellow taxi tends to travel in two’s and three’s the most.*
- *Most number of trips recorded had passengers travelling less than 30 miles, which makes sense as yellow taxis are commonly used for short trips within NYC.*
- *Similarly average trip duration lies within fifty minutes.*

Scatter Matrix Plot (Raw Data):

![Image of Plot](Images/scatter1.png)


Scatter Matrix Plot (Final Data):

![Image of Plot](Images/scatter12.png)

#### Heatmap (Monthly vs Weekly)

```
heatmap_df1["Month"] = pd.Categorical(heatmap_df1["Month"], heatmap_df1.Month.unique()) 
plt.figure(figsize = (15, 9)) # Assigning figure size (length & breadth) for the plot
file_long = heatmap_df1.pivot("Weekday", "Month", "Crash_Count") # Assigning the column names for which the heatmap needs to be plotted
sns.heatmap(file_long, cmap = 'viridis', annot=True, fmt=".0f") # Plotting the map
plt.title("Heatmap of Crash Count in New York City (Monthly vs Weekly)", fontsize = 14); # Assigning title for the plot
plt.savefig('Heatmap1.jpg') # Saving the plot
```
The output from this code is shown below:
![Image of Plot](images/Heatmap1.jpg)

#### Heatmap (Weekly vs Hourly)
```
heatmap_df2["Weekday"] = pd.Categorical(heatmap_df2["Weekday"], heatmap_df2.Weekday.unique())
plt.figure(figsize = (20, 10))
file_long = heatmap_df2.pivot("Weekday", "Hour", "Crash_Count")
sns.heatmap(file_long, cmap = 'viridis', annot=True, fmt=".0f")
plt.title("Heatmap of Crash Count in New York City (Weekly vs Hourly)", fontsize = 14);
plt.savefig('Heatmap2.jpg')
```

The output from this code is shown below:
![Image of Plot](images/Heatmap2.jpg)

#### GMAPS Heatmap on NYC

```
#------------------------Visualizing using Gmaps-------------------------------

locations=pd.DataFrame(results_df[['latitude','longitude']])
locations[['latitude','longitude']] = locations[['latitude','longitude']].astype(float) #Latitude and Longitude data are stored as float

gmaps.configure(api_key='Key Here') #GMAPS API key is inserted
nyc_coordinates = (40.7128, -74.0060)
fig = gmaps.figure(center=nyc_coordinates, zoom_level=10.5) #Map co-ordinates along with zoom level is set
heatmap_layer=gmaps.heatmap_layer(locations) #heatmap layer is created using latitude,longitude
heatmap_layer.max_intensity = 200
heatmap_layer.point_radius = 15
fig.add_layer(heatmap_layer)
embed_minimal_html('Heatmap_layer.html', views=[fig]) #heatmap file is exported in save directory
```

The output from this code is shown below:
![Image of Plot](images/map.png)

---

## How to Run the Code
### Using Terminal
*1. Open a terminal window.*

*2. Change directories to where `API_NYC_crashdata.py` is saved.*

*3. Type the following command:*
	```
	python API_NYC_crashdata.py
	```
    
### Using Spyder/ Jupyter
*1. Click on File->Open*

*2. Choose directory where `API_NYC_crashdata.py` is stored*

*3. Click on run or press F5 on Spyder, Shift+Enter in Jupyter*

---

## Suggestions
Weather data can be added to understand how the weather influences different contributing factors of the accidents. It can also be used to understand the severity of accidents with respect to different weather conditions.

GMAPS Visualization Modification:
Maps of different type can be set using a parameter```map_type=Hybrid/Satellite``` in ```gmaps.figure``` . Markers can be set to the map using the following code ```gmaps.marker_layer```
