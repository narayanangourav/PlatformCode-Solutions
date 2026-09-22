# Weather Observation Station 4

<!-- synced-problem-statement -->

Find the difference between the total number of **CITY** entries in the table and the number of distinct **CITY** entries in the table.  
The **STATION** table is described as follows:

<img src="https://s3.amazonaws.com/hr-challenge-images/9336/1449345840-5f0a551030-Station.jpg" title="Station.jpg" />

where **LAT\_N** is the northern latitude and **LONG\_W** is the western longitude.

For example, if there are three records in the table with **CITY** values 'New York', 'New York', 'Bengalaru', there are 2 different city names: 'New York' and 'Bengalaru'.  The query returns $1$, because $\text{total number of records} - \text{number of unique city names} = 3 - 2 = 1$.

Source: https://www.hackerrank.com/challenges/weather-observation-station-4/problem
