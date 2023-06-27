import math
import pandas as pd
import geopandas as gpd
from uszipcode import SearchEngine
import statistics
from census import Census
from us import states

# imports precinct level dataset
tx_df = pd.read_csv("Texas_Precinct_Election_Data.csv")

# imports shapefile of Texas Precincts
tx_gdf = gpd.read_file("TX_Precincts_Shapefile//VTDs_22G.shp", encoding="utf-8")

# finds the area of each precinct in square miles
tx_df['Area'] = (tx_gdf['Shape_area'] / 10 ** 6 / 2.58999)

# creates a new dataframe of ZIP Codes from precincts
tx_zips = tx_df.groupby("ZIP_Code").sum()
tx_zips['Metro'] = tx_df.groupby("ZIP_Code")['Metro']
tx_zips = tx_zips[['Total_Votes_2020_Pres', 'Total_Votes_2022_Gov', 'Trump_2020_Votes', 'Biden_2020_Votes',
                   'Abbott_2022_Votes', 'O_Rourke_2022_Votes', 'VAP_2022', 'Area']]

# adds new columns
tx_zips['Trump_2020_Pct'] = tx_zips['Trump_2020_Votes'] / tx_zips['Total_Votes_2020_Pres'] * 100
tx_zips['Biden_2020_Pct'] = tx_zips['Biden_2020_Votes'] / tx_zips['Total_Votes_2020_Pres'] * 100
tx_zips['Abbott_2022_Pct'] = tx_zips['Abbott_2022_Votes'] / tx_zips['Total_Votes_2022_Gov'] * 100
tx_zips['O_Rourke_2022_Pct'] = tx_zips['O_Rourke_2022_Votes'] / tx_zips['Total_Votes_2022_Gov'] * 100
tx_zips["Dem_Margin_2020_Pres_Pct"] = tx_zips["Biden_2020_Pct"] - tx_zips["Trump_2020_Pct"]
tx_zips["Dem_Margin_2022_Gov_Pct"] = tx_zips["O_Rourke_2022_Pct"] - tx_zips["Abbott_2022_Pct"]
tx_zips["Dem_Margin_Gain_Pct"] = tx_zips["Dem_Margin_2022_Gov_Pct"] - tx_zips["Dem_Margin_2020_Pres_Pct"]
tx_zips["Dem_Raw_Vote_Gain"] = tx_zips["O_Rourke_2022_Votes"] - tx_zips["Biden_2020_Votes"]
tx_zips["GOP_Raw_Vote_Gain"] = tx_zips["Abbott_2022_Votes"] - tx_zips["Trump_2020_Votes"]
tx_zips["Dem_Raw_Vote_Margin_Gain"] = tx_zips["Dem_Raw_Vote_Gain"] - tx_zips["GOP_Raw_Vote_Gain"]
tx_zips["Change_in_Turnout"] = (tx_zips["Total_Votes_2022_Gov"] / tx_zips["Total_Votes_2020_Pres"] - 1)\
                                    * 100
tx_zips['Pop_Density'] = tx_zips['VAP_2022'] / tx_zips['Area']


# cities with a population of more than 500,000
tx_big_cities = ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso']

search = SearchEngine()
community_types = []
# finds out the community type for each ZIP Code
for zip_code, row in tx_zips.iterrows():
    city = search.by_zipcode(int(zip_code)).to_dict()['major_city']
    if city in tx_big_cities:
        community_types.append("Big City")
    else:
        metros = list(tx_df[tx_df['ZIP_Code'] == zip_code]["Metro"])
        metro = statistics.mode(metros)
        if metro in tx_big_cities or metro == 'Dallas-Fort Worth':
            # 389.5 takes 500 people per square mile (USDA assessment of rural population density) and multiplies it
            # with the share of adults in the US (77.9%)
            if row['Pop_Density'] > 389.5:
                community_types.append('Big City Suburb')
            else:
                community_types.append('Rural or Small City Suburb')
        else:
            if row['Pop_Density'] > 389.5:
                community_types.append('Small City')
            else:
                community_types.append('Rural or Small City Suburb')
tx_zips['Community_Type'] = community_types

# uses the Census library to get educational attainment and median household income data
c = Census("a0b4141eefc903f9a739570f8c1f004f8f705b35")

tx_census = c.acs5.state_zipcode(fields=('NAME', 'B15003_022E', 'B15003_023E', 'B15003_024E', 'B15003_025E',
                                         'B15003_001E', 'B19013_001E'),
                                 state_fips=states.TX.fips,
                                 state='*',
                                 zcta='*',
                                 year=2020)
tx_census_data = pd.DataFrame(tx_census)

# calculates the percentage of people in each ZIP Code who hold at least a bachelor's degree
tx_census_data['Bachelor_Degree_or_Higher_25_&_Older_Pct'] = (tx_census_data['B15003_022E'] +
                                                              tx_census_data['B15003_023E'] +
                                                              tx_census_data['B15003_024E'] +
                                                              tx_census_data['B15003_025E']) / \
                                                              tx_census_data['B15003_001E'] * 100
tx_census_data = tx_census_data.rename(columns={'B19013_001E': 'Median_Household_Income_2020',
                                                'zip code tabulation area': 'ZIP_Code'})
tx_census_data['ZIP_Code'] = tx_census_data['ZIP_Code'].astype(float)

# merges the two dataframes
tx_zips = tx_zips.reset_index()
tx_zip_code_data = tx_zips.merge(tx_census_data, how='left')

# assigns NA values to ZIP codes that report a negative median household income
tx_zip_code_data['Median_Household_Income_2020'] = tx_zip_code_data['Median_Household_Income_2020'].map(
    lambda x: math.nan if x < 0 else x)

# removes unnecessary columns
tx_zip_code_data.drop(tx_zip_code_data.columns[list(range(22, 28))], axis=1, inplace=True)

# exports DataFrame to a csv file
tx_zip_code_data.to_csv("Texas_ZIP_Code_Data.csv", index=False, header=True)