library(ggplot2)
data <- read.csv("Texas_Precinct_Election_Data.csv")
head(data)
ggplot(data = data, aes(x = White_VAP_2022/VAP_2022,  y1 = Biden_2020_Votes / Total_Votes_2020_Pres, y2 = Trump_2020_Votes / Total_Votes_2020_Pres)) + geom_point(aes(y = Biden_2020_Votes / Total_Votes_2020_Pres), color='blue', position = "jitter", size = 1, alpha = 0.05) + geom_point(aes(y = Trump_2020_Votes / Total_Votes_2020_Pres), color='red', position = "jitter", size = 1, alpha = 0.05)
