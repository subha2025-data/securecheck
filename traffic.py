# Project Title - SecureCheck: A Python-SQL Digital Ledger for Police Post Logs
# Skills take away From This Project - 
# Python, SQL, Streamlit
# Step - 1 Import the libraries
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import psycopg2
# step - 2 load the data set
# Read the Excel File
traffic_df = pd.read_excel(r"C:\Users\Vignesh\Downloads\traffic_stops.xlsx", engine='openpyxl')
# Displace the first few rows
traffic_df.head()
# Check the data types of the columns
traffic_df.dtypes
# Join the two columns stop_date and stop_time in the single column of stop_datetime
traffic_df['stop_datetime'] = pd.to_datetime(traffic_df['stop_date'].astype(str) + ' ' + traffic_df['stop_time'].astype(str), errors='coerce')
# Drop those two columns 
traffic_df.drop(['stop_date', 'stop_time'], axis=1, inplace=True)
traffic_df.head()
# Check the Null values
traffic_df.isnull().sum()
traffic_df['search_type'].value_counts(dropna=False)
# Drop the Null value rows
traffic_df.dropna(subset=['search_type'], inplace=True)
# Check the data types
traffic_df.dtypes
traffic_df.head()
# step - 4 SQL Connection
# Using sqlalchemy
from sqlalchemy import create_engine
# step - 5 PostgreSQL connection
user = "postgres"
password = "subhapost1234"
host = "localhost"
port = "5432"  # default port
database = "traffic_data"

# Create connection string
engine = create_engine(f'postgresql+psycopg2://postgres:subhapost1234@localhost:5432/traffic_data')
#  step - 6 Inserting a Date into the table using to_sql() (pandas + SQLalchemy)
traffic_df.to_sql('traffic_data', engine, index=False, if_exists='replace')
# step - 7 Read the traffic_data 
Query='SELECT * FROM traffic_data' 
new_traffic_df=pd.read_sql(Query, engine)
new_traffic_df
# step - 8 Running the SQL Queries
#  Vehicle-Based
# Q.no 1.What are the top 10 vehicle_Number involved in drug-related stops?

top_10_vehicles = (
    traffic_df[traffic_df['drugs_related_stop'] == True]
    .groupby('vehicle_number')
    .size()
    .sort_values(ascending=False)
    .head(10)
)

print(top_10_vehicles)

# Q.No 2. Which vehicles were most frequently searched? 

most_searched_vehicles = (
    traffic_df[traffic_df['search_conducted'] == True]
    .groupby('vehicle_number')
    .size()
    .sort_values(ascending=False)
    .head(10)
)

print(most_searched_vehicles)

# Q.No 3. Which driver age group had the highest arrest rate?

# Define age bins and labels
bins = [0, 18, 25, 35, 50, 65, 100]
labels = ['<18', '18-25', '26-35', '36-50', '51-65', '65+']

# Create a new column 'age_group'
traffic_df['age_group'] = pd.cut(traffic_df['driver_age'], bins=bins, labels=labels, right=False)

# Group by age_group and calculate arrest rate
arrest_rate = (
    traffic_df.groupby('age_group')['is_arrested']
    .mean()
    .sort_values(ascending=False)
)

print(arrest_rate)

# Q.N0 4. What is the gender distribution of drivers stopped in each country?

gender_dist = (
    traffic_df
    .groupby(['country_name', 'driver_gender'])
    .size()
    .reset_index(name='stop_count')
    .sort_values(['country_name', 'stop_count'], ascending=[True, False])
)

print(gender_dist)

# Q.NO 5. Which race and gender combination has the highest search rate?

search_rate = (
    traffic_df
    .groupby(['driver_race', 'driver_gender'])['search_conducted']
    .mean()
    .sort_values(ascending=False)
)

# Display the top combination with highest search rate
print(search_rate.head(1))

# Q.No 6. What time of day sees the most traffic stops?

# Step 1: Extract hour from datetime
traffic_df['hour'] = traffic_df['stop_datetime'].dt.hour

# Step 2: Define time of day
def time_of_day(hour):
    if 5 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 16:
        return 'Afternoon'
    elif 17 <= hour <= 20:
        return 'Evening'
    else:
        return 'Night'

traffic_df['time_of_day'] = traffic_df['hour'].apply(time_of_day)

# Step 3: Count traffic stops by time of day
traffic_by_time = traffic_df['time_of_day'].value_counts().sort_values(ascending=False)

print(traffic_by_time)

# Q.No 7. What is the average stop duration for different violations?

# Step 1: Map durations to numeric (in minutes)
duration_map = {
    '0-15 Min': 7.5,
    '16-30 Min': 23,
    '30+ Min': 35
}

traffic_df['stop_duration_min'] = traffic_df['stop_duration'].map(duration_map)

# Step 2: Group by violation and get average
avg_duration = (
    traffic_df
    .groupby('violation')['stop_duration_min']
    .mean()
    .sort_values(ascending=False)
)

print(avg_duration)

# Q.No 8. Are stops during the night more likely to lead to arrests?

# Define night as 8 PM to 6 AM
traffic_df['is_night'] = traffic_df['stop_datetime'].dt.hour.apply(lambda h: h >= 20 or h < 6)

# Group by night/day and calculate arrest rate
arrest_rates = traffic_df.groupby('is_night')['is_arrested'].mean().reset_index()

# Rename columns for clarity
arrest_rates.columns = ['is_night', 'arrest_rate']

print(arrest_rates)

# Q.no 9. Which violations are most associated with searches or arrests?

# Group by violation and calculate average search and arrest rates
violation_stats = traffic_df.groupby('violation').agg(
    search_rate=('search_conducted', 'mean'),
    arrest_rate=('is_arrested', 'mean'),
    total_stops=('violation', 'count')  # Optional: show volume
).reset_index()

# Sort to see highest rates at top (optional)
violation_stats = violation_stats.sort_values(by=['search_rate', 'arrest_rate'], ascending=False)

print(violation_stats)

# Q.no 10. Which violations are most common among younger drivers (<25)?

# Filter younger drivers
young_drivers = traffic_df[traffic_df['driver_age'] < 25]

# Group by violation and count
young_violation_counts = young_drivers['violation'].value_counts().reset_index()
young_violation_counts.columns = ['violation', 'stop_count']

print(young_violation_counts)

# Q.no 11. Is there a violation that rarely results in search or arrest?

# Group by violation and calculate search/arrest rates
violation_stats = traffic_df.groupby('violation').agg(
    search_rate=('search_conducted', 'mean'),
    arrest_rate=('is_arrested', 'mean'),
    total_stops=('violation', 'count')
).reset_index()

# Filter violations with low search and arrest rates (e.g., < 0.01 or 1%)
low_action_violations = violation_stats[
    (violation_stats['search_rate'] < 0.01) & 
    (violation_stats['arrest_rate'] < 0.01)
]

print(low_action_violations)

# Q.no 12. Which countries report the highest rate of drug-related stops?

# Group by country and calculate drug-related stop rate
drug_rate_by_country = traffic_df.groupby('country_name').agg(
    drug_stop_rate=('drugs_related_stop', 'mean'),
    total_stops=('drugs_related_stop', 'count')
).reset_index()

# Sort by highest drug stop rate
drug_rate_by_country = drug_rate_by_country.sort_values(by='drug_stop_rate', ascending=False)

print(drug_rate_by_country)

# Q.no 13. What is the arrest rate by country and violation?

# Group by country and violation, calculate arrest rate
arrest_rate = traffic_df.groupby(['country_name', 'violation']).agg(
    arrest_rate=('is_arrested', 'mean'),
    total_stops=('is_arrested', 'count')
).reset_index()

# Optional: sort by arrest rate
arrest_rate = arrest_rate.sort_values(by='arrest_rate', ascending=False)

print(arrest_rate)

# Q.no 14. Which country has the most stops with search conducted? 

# Filter for search conducted
search_df = traffic_df[traffic_df['search_conducted'] == True]

# Group by country and count
search_counts = search_df['country_name'].value_counts().reset_index()
search_counts.columns = ['country_name', 'search_count']

# Get the country with the most searches
most_searches = search_counts.iloc[0]

print(search_counts)       # To see all countries
print(most_searches)       # To see the top country only

# Q.no 15. Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)

# Extract year from datetime
traffic_df['year'] = traffic_df['stop_datetime'].dt.year

# Group by country and year
yearly_stats = traffic_df.groupby(['country_name', 'year']).agg(
    total_stops=('is_arrested', 'count'),
    total_arrests=('is_arrested', 'sum')
).reset_index()

# Calculate arrest rate
yearly_stats['arrest_rate'] = yearly_stats['total_arrests'] / yearly_stats['total_stops']

# Use groupby().transform() for window-like share calculation
yearly_stats['country_share_of_yearly_stops'] = (
    100 * yearly_stats['total_stops'] /
    yearly_stats.groupby('year')['total_stops'].transform('sum')
).round(2)

print(yearly_stats.sort_values(['year', 'country_name']))

# Q.no 16. Driver Violation Trends Based on Age and Race (Join with Subquery)

# Create age groups
def age_group(age):
    if age < 25:
        return '<25'
    elif 25 <= age <= 44:
        return '25-44'
    else:
        return '45+'

traffic_df['age_group'] = traffic_df['driver_age'].apply(age_group)

# Group by age group, race, and violation
violation_trends = traffic_df.groupby(['age_group', 'driver_race', 'violation']).size().reset_index(name='stop_count')

# Sort for readability
violation_trends = violation_trends.sort_values(by=['age_group', 'driver_race', 'stop_count'], ascending=[True, True, False])

print(violation_trends)

# Q.no 17. Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day

# Extract time parts
traffic_df['year'] = traffic_df['stop_datetime'].dt.year
traffic_df['month'] = traffic_df['stop_datetime'].dt.to_period('M').astype(str)
traffic_df['hour'] = traffic_df['stop_datetime'].dt.hour

# A) Stops by Year
stops_by_year = traffic_df['year'].value_counts().sort_index().reset_index()
stops_by_year.columns = ['year', 'total_stops']

# B) Stops by Month
stops_by_month = traffic_df['month'].value_counts().sort_index().reset_index()
stops_by_month.columns = ['month', 'total_stops']

# C) Stops by Hour
stops_by_hour = traffic_df['hour'].value_counts().sort_index().reset_index()
stops_by_hour.columns = ['hour', 'total_stops']

print("Stops by Year:\n", stops_by_year)
print("Stops by Month:\n", stops_by_month)
print("Stops by Hour:\n", stops_by_hour)

# Q.no 18.Violations with High Search and Arrest Rates (Window Function)

# Group by violation and calculate search and arrest rates
violation_rates = traffic_df.groupby('violation').agg(
    search_rate=('search_conducted', 'mean'),
    arrest_rate=('is_arrested', 'mean')
).reset_index()

# Rank using pandas' rank method
violation_rates['search_rank'] = violation_rates['search_rate'].rank(method='min', ascending=False)
violation_rates['arrest_rank'] = violation_rates['arrest_rate'].rank(method='min', ascending=False)

# Filter: top 3 in either search or arrest rank
top_violations = violation_rates[
    (violation_rates['search_rank'] <= 3) | 
    (violation_rates['arrest_rank'] <= 3)
].sort_values(by=['search_rank', 'arrest_rank'])

print(top_violations)

# Q.no 19. .Driver Demographics by Country (Age, Gender, and Race)

# Group by country and calculate average age
demo_stats = traffic_df.groupby('country_name').agg(
    avg_driver_age=('driver_age', 'mean'),
    total_stops=('driver_age', 'count')
).reset_index()

# Gender distribution by country
gender_counts = pd.crosstab(traffic_df['country_name'], traffic_df['driver_gender'], normalize='index') * 100
race_counts = pd.crosstab(traffic_df['country_name'], traffic_df['driver_race'], normalize='index') * 100

# Combine everything
demographics = demo_stats.join(gender_counts, on='country_name')
demographics = demographics.join(race_counts, on='country_name')

# Round for readability
demographics = demographics.round(1)

print(demographics)

# Q.no 20. Top 5 Violations with Highest Arrest Rates

# Group by violation and calculate total stops and arrest rate
violation_arrest_rate = traffic_df.groupby('violation').agg(
    total_stops=('is_arrested', 'count'),
    total_arrests=('is_arrested', 'sum'),
    arrest_rate=('is_arrested', 'mean')
).reset_index()

# Sort and get top 5
top_5_arrests = violation_arrest_rate.sort_values(by='arrest_rate', ascending=False).head(5)

# Optional: round for display
top_5_arrests = top_5_arrests.round(3)

print(top_5_arrests)


