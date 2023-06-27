import math
import numpy as np
import time
import pandas as pd
import geopandas as gpd
import folium

# imports shapefile of Texas Precincts
tx_gdf = gpd.read_file("TX_Precincts_Shapefile//VTDs_22G.shp", encoding="utf-8")

# imports precinct level dataset
tx_df = pd.read_csv("Texas_Precinct_Election_Data.csv")

# changes crs and finds the geographic center and area of the precinct
tx_gdf = tx_gdf.to_crs(epsg=4326)
tx_gdf["Center"] = tx_gdf.to_crs('+proj=cea').centroid.to_crs(epsg=4326)
tx_gdf["Lat_C"] = tx_gdf["Center"].map(lambda p: p.y)
tx_gdf["Long_C"] = tx_gdf["Center"].map(lambda p: p.x)
precinct_centers = tx_gdf[['CNTYVTD', 'Lat_C', 'Long_C']].set_index('CNTYVTD')

# converts geodata to json for mapping
precincts = gpd.GeoSeries(tx_gdf.set_index('CNTYVTD')['geometry']).to_json()
print("Pre-Mapping finished")

# Creates 3 maps
map_1 = folium.Map(location=[31.21, -99.14], tiles='cartodbpositron', zoom_start=6)
map_2 = folium.Map(location=[31.21, -99.14], tiles='cartodbpositron', zoom_start=6)
map_3 = folium.Map(location=[31.21, -99.14], tiles='cartodbpositron', zoom_start=6)

# This changes outlier values to help with mapping. The original dataset still has the correct values
def revalue_df(row):
    if row['Dem_Margin_Gain_Pct'] > 20:
        row['Dem_Margin_Gain_Pct'] = 20
    elif row['Dem_Margin_Gain_Pct'] < -20:
        row['Dem_Margin_Gain_Pct'] = -20
    if row["Change_in_Turnout"] < -50:
        row["Change_in_Turnout"] = -50
    elif row["Change_in_Turnout"] > 50:
        row["Change_in_Turnout"] = 50
    return row

tx_df = tx_df.apply(revalue_df, axis='columns')



folium.Choropleth(geo_data=precincts,
                  name='choropleth',
                  data=tx_df,
                  columns=['CNTYVTD', 'Dem_Margin_Gain_Pct'],
                  key_on="feature.id",
                  fill_color='RdBu',
                  fill_opacity=0.5,
                  line_opacity=0.1,
                  highlight=True,
                  bins=[-20, -10, -5, -2.5, 0, 2.5, 5, 10, 20],
                  legend_name='Dem Margin (%) Change from 2020'
                  ).add_to(map_1)
print('Finished Map 1')

folium.Choropleth(geo_data=precincts,
                  name='choropleth',
                  data=tx_df[tx_df["Change_in_Turnout"] != np.inf],
                  columns=['CNTYVTD', 'Change_in_Turnout'],
                  key_on="feature.id",
                  fill_color='RdYlGn',
                  fill_opacity=0.5,
                  line_opacity=0.1,
                  highlight=True,
                  bins=8,
                  legend_name='Turnout Change from 2020 (%)'
                  ).add_to(map_2)
print('Finished Map 2')



def color_producer(val):
    if val < 0:
        return 'red'
    else:
        return 'blue'

def radius_value(val):
    return math.sqrt(abs(val) / math.pi) / 2

for idx, row in tx_df.iterrows():
    vtd = row["CNTYVTD"]
    # gets the center of the precinct
    lat = precinct_centers.loc[vtd]["Lat_C"]
    long = precinct_centers.loc[vtd]["Long_C"]
    dem_vote_margin_change = (row["O_Rourke_2022_Votes"] - row["Abbott_2022_Votes"]) - 8106768 / 11317052 * \
                             (row["Biden_2020_Votes"] - row["Trump_2020_Votes"])
    if dem_vote_margin_change != 0:
        popup_text = "Adjusted Dem Vote Gain: " + str(round(dem_vote_margin_change))
        folium.CircleMarker(
            location=[lat, long], radius=radius_value(dem_vote_margin_change),
            popup=popup_text,
            color=color_producer(dem_vote_margin_change), fill=True).add_to(map_3)


print('Finished Map 3')


# Saves the Maps to html
map_1.save("Map_1.html")
map_2.save("Map_2.html")
map_3.save("Map_3.html")
