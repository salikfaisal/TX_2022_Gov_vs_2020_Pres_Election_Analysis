import pandas as pd
import time

# imports list of Texas Precincts
tx_precincts = pd.read_csv("List_of_Precincts_in_Texas.csv")

# imports 2020 and 2022 Election Results
results_2020 = pd.read_csv("2020_General_Election_Returns.csv")
results_2022 = pd.read_csv("2022_General_Election_Returns.csv")

# imports demographic data for every precinct
tx_pop_data = pd.read_csv("VTDs_22G_Pop.csv")

# imports county data
tx_county_data = pd.read_csv("TX_Counties.csv")
tx_county_data = tx_county_data.set_index("County")

# filters election results for only President in 2020 and Governor in 2022
pres_2020_results = results_2020[results_2020["Office"] == 'President']
gov_2022_results = results_2022[results_2022["Office"] == 'Governor']

# capitalizes precincts with letters
pres_2020_results.loc[:, "cntyvtd"] = pres_2020_results["cntyvtd"].map(lambda p: p.upper())
gov_2022_results.loc[:, "cntyvtd"] = gov_2022_results["cntyvtd"].map(lambda p: p.upper())

# Lists to add to dataframe
county_region = []
metro_area = []
border_area = []
total_2020_pres_votes = []
total_2022_gov_votes = []
trump_2020_votes = []
biden_2020_votes = []
abbott_2022_votes = []
o_rourke_2022_votes = []
total_vap_2022 = []
white_vap_2022 = []
latino_vap_2022 = []
black_vap_2022 = []
asian_vap_2022 = []

# useful to keep track of time
start_time = time.time()

# pulls data from other datasets and adds it to the lists above
for count, precinct in tx_precincts.iterrows():
    vtd = precinct["CNTYVTD"]
    precinct_2020_pres_results = pres_2020_results[pres_2020_results["cntyvtd"] == vtd]
    precinct_2022_gov_results = gov_2022_results[gov_2022_results["cntyvtd"] == vtd]
    # Adds County Data
    county = precinct_2020_pres_results.iloc[0]["County"]
    county_region.append(tx_county_data.loc[county]["Region"])
    metro_area.append(tx_county_data.loc[county]["Metro"])
    border_area.append(tx_county_data.loc[county]["Border"])
    # Adds Precinct Vote Totals for major party candidates in both elections
    total_2020_pres_votes.append(precinct_2020_pres_results["Votes"].sum())
    total_2022_gov_votes.append(precinct_2022_gov_results["Votes"].sum())
    trump_2020_votes.append(precinct_2020_pres_results[precinct_2020_pres_results["Name"] == "Trump"].iloc[0]["Votes"])
    biden_2020_votes.append(precinct_2020_pres_results[precinct_2020_pres_results["Name"] == "Biden"].iloc[0]["Votes"])
    abbott_2022_votes.append(precinct_2022_gov_results[precinct_2022_gov_results["Name"] == "Abbott"].iloc[0]["Votes"])
    o_rourke_2022_votes.append(
        precinct_2022_gov_results[precinct_2022_gov_results["Name"] == "O'Rourke"].iloc[0]["Votes"])
    # adds demographic data for the Voting Age Population in the Precinct
    pop_data = tx_pop_data[tx_pop_data["CNTYVTD"] == vtd].iloc[0]
    total_vap_2022.append(pop_data["vap"])
    white_vap_2022.append(pop_data["anglovap"])
    latino_vap_2022.append(pop_data["hispvap"])
    black_vap_2022.append(pop_data["blackvap"])
    asian_vap_2022.append(pop_data["asianvap"])
    # for time estimation purposes
    if count % 100 == 0:
        print(round((count + 1) / 9634 * 100, 1), "% complete")
        end_time = time.time()
        time_so_far = (end_time - start_time) / 60
        time_when_finished = time_so_far / (count + 1) * 9634
        print(round(time_when_finished - time_so_far, 2), "minutes left")
print("Completed in", round(time_so_far, 2), "minutes")

# adds new columns from lists in the tx_gdf GeoDataFrame
tx_precincts["Region"] = county_region
tx_precincts["Metro"] = metro_area
tx_precincts["Border"] = border_area
tx_precincts["Total_Votes_2020_Pres"] = total_2020_pres_votes
tx_precincts["Total_Votes_2022_Gov"] = total_2022_gov_votes
tx_precincts["Trump_2020_Votes"] = trump_2020_votes
tx_precincts["Biden_2020_Votes"] = biden_2020_votes
tx_precincts["Abbott_2022_Votes"] = abbott_2022_votes
tx_precincts["O_Rourke_2022_Votes"] = o_rourke_2022_votes
tx_precincts["VAP_2022"] = total_vap_2022
tx_precincts["White_VAP_2022"] = white_vap_2022
tx_precincts["Latino_VAP_2022"] = latino_vap_2022
tx_precincts["Black_VAP_2022"] = black_vap_2022
tx_precincts["Asian_VAP_2022"] = asian_vap_2022
tx_precincts["Biden_2020_Pct"] = tx_precincts["Biden_2020_Votes"] / tx_precincts["Total_Votes_2020_Pres"] * 100
tx_precincts["Trump_2020_Pct"] = tx_precincts["Trump_2020_Votes"] / tx_precincts["Total_Votes_2020_Pres"] * 100
tx_precincts["Abbott_2022_Pct"] = tx_precincts["Abbott_2022_Votes"] / tx_precincts["Total_Votes_2022_Gov"] * 100
tx_precincts["O_Rourke_2022_Pct"] = tx_precincts["O_Rourke_2022_Votes"] / tx_precincts["Total_Votes_2022_Gov"] * 100
tx_precincts["White_VAP_2022_Pct"] = tx_precincts["White_VAP_2022"] / tx_precincts["VAP_2022"] * 100
tx_precincts["Latino_VAP_2022_Pct"] = tx_precincts["Latino_VAP_2022"] / tx_precincts["VAP_2022"] * 100
tx_precincts["Black_VAP_2022_Pct"] = tx_precincts["Black_VAP_2022"] / tx_precincts["VAP_2022"] * 100
tx_precincts["Asian_VAP_2022_Pct"] = tx_precincts["Asian_VAP_2022"] / tx_precincts["VAP_2022"] * 100
tx_precincts["Dem_Margin_2020_Pres_Pct"] = tx_precincts["Biden_2020_Pct"] - tx_precincts["Trump_2020_Pct"]
tx_precincts["Dem_Margin_2022_Gov_Pct"] = tx_precincts["O_Rourke_2022_Pct"] - tx_precincts["Abbott_2022_Pct"]
tx_precincts["Dem_Margin_Gain_Pct"] = tx_precincts["Dem_Margin_2022_Gov_Pct"] - tx_precincts["Dem_Margin_2020_Pres_Pct"]
tx_precincts["Dem_Raw_Vote_Gain"] = tx_precincts["O_Rourke_2022_Votes"] - tx_precincts["Biden_2020_Votes"]
tx_precincts["GOP_Raw_Vote_Gain"] = tx_precincts["Abbott_2022_Votes"] - tx_precincts["Trump_2020_Votes"]
tx_precincts["Dem_Raw_Vote_Margin_Gain"] = tx_precincts["Dem_Raw_Vote_Gain"] - tx_precincts["GOP_Raw_Vote_Gain"]
tx_precincts["Change_in_Turnout"] = (tx_precincts["Total_Votes_2022_Gov"] / tx_precincts["Total_Votes_2020_Pres"] - 1)\
                                    * 100



# exports DataFrame to a csv file
tx_precincts.to_csv("Texas_Precinct_Election_Data.csv", index=False, header=True)