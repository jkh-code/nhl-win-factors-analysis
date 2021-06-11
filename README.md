# Analysis of Regular Season Win Factors in the NHL

## Table of Contents
- [Background](#background)
- [Data](#data)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Hypothesis Testing](#hypothesis-testing)
- [Future Analysis](#future-analysis)

## Background
The National Hockey League (NHL) is one of the four major professional sports organizations in North America. Like all sports organizations, the NHL has been hurt by the global COVID-19 pandemic. There has been lost revenue and lost interest in sports. However, as of early June 2021, North America appears to be making a recovery as more and more of the economy reopens. The economy opening up means sports leagues, like the NHL, can invite fans back to their stadiums when their seasons resume. However, with reopening comes a question: how will NHL teams bring fans back to stadiums and keep them engaged with their sport and team? The best way is by winning. Nothings brings in fans like winning. My goal is to answer what features reliably result in winning NHL regular season games.

## Data
The NHL provides game-level data through their [website](http://www.nhl.com/stats/teams). These data include 23 features such as team name, date of game, opponent, was the game a win or a loss, the type of win, and summary game statistics for games going back to the 1917 season. This analysis will focus on a 10 year period between the 2009-2010 and 2018-2019 seasons. This time period was examined to remove any impact the COVID-19 pandemic may have had on performance between the 2019 and 2020 seasons and because this is a recent enough sample to make claims about successful games in the near future.

The dataset for this project was scraped from the NHL website using [Selenium](https://www.selenium.dev/), [ChromeDriver](https://chromedriver.chromium.org/), and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/); raw data was stored in a MongoDB collection; and the processed data was stored in a PostgreSQL database. There are 23,444 records from the 10 year period.

| Field  | Description |
| ------------- | ------------- |
| Team  | Team name  |
| Game | Date, at or versus, and opponent |
| GP  | Games played |
| W  | Win |
| L  | Loss |
| T  | Tie |
| OT  | Overtime win |
| P  | Points |
| P%  | Point Percentage |
| RW  | Regulation win |
| ROW  | Regulation and overtime wins |
| S/O Win  | Shootout win |
| GF  | Goals for |
| GA  | Goals against |
| GF/GA  | Goals for by goals against |
| GA/GP  | Goals against by games played |
| PP%  | Power play percent |
| PK%  | Penalty kill percent |
| Net PP%  | Net power play percent |
| Net PK%  | Net penalty kill percent |
| Shots/GP  | Shots per game |
| SA/GP  | Shots against per game |
| FOW%  | Face-Off win percentage |

## Exploratory Data Analysis


## Hypothesis Testing


## Future Analysis








<center>
<img src="./images/cum-perc-wins-pp.png" width="49%"/> <img src="./images/cum-perc-wins-pp.png" width="49%"/> 
</center>