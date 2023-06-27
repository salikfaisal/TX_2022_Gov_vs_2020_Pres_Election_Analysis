# Imports data
library(ggplot2)
library(tidyr)
library(ggalt)
library(viridis)
precinct_data <- read.csv("Texas_Precinct_Election_Data.csv")
zip_code_data <- read.csv("Texas_ZIP_Code_Data.csv")
# adjusts the change in margin for differences in OVERALL turnout between the elections
precinct_data["Adjusted_Dem_Vote_Gain"] <- (precinct_data$O_Rourke_2022_Votes - precinct_data$Abbott_2022_Votes) - 8106768 / 11317052 * (precinct_data$Biden_2020_Votes - precinct_data$Trump_2020_Votes)

zip_code_data["Adjusted_Dem_Vote_Gain"] <- (zip_code_data$O_Rourke_2022_Votes - zip_code_data$Abbott_2022_Votes) - 8106768 / 11317052 * (zip_code_data$Biden_2020_Votes - zip_code_data$Trump_2020_Votes)
# Figure 1
ggplot(data = precinct_data, aes(x = (100 - White_VAP_2022_Pct), y = Change_in_Turnout)) + geom_point(size = 1, alpha = 0.1, color = 'purple') + geom_smooth(method = 'lm', color = 'purple') + labs(title = "Change in Voter Turnout from 2020 to 2022 (Precinct-Level)", x = "Percentage of Non-White Voters", y = "Change in Turnout (%)") + ylim(-75, 25) + theme(plot.title=element_text(hjust=0.5))
