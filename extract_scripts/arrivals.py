import datetime as dt
import json
import os
import re
from os import path

import pandas as pd
import requests
from pandas import Series
from pandas.io.json import json_normalize

from utils.tools import create_dir

pd.set_option('display.max_columns', 150)
pd.set_option('display.width', 150)

PARENT_PATH = path.dirname(__file__)
ROOT_PATH = path.abspath(path.join(PARENT_PATH, '..'))
ROOTER_PATH = path.abspath(path.join(PARENT_PATH, '..', ".."))

DBT_DATA_DIR = path.join(ROOT_PATH, 'dbt/data')
OUTPUT_DIR = path.join(PARENT_PATH, 'output')

HEADERS: [
    'Airport_ID',
    'Name',
    'City',
    'Country',
    'IATA',
    'ICAO',
    'Latitude',
    'Longitude',
    'Altitude',
    'Timezone',
    'DST',
    'database_time_zone',
    'Type',
    'Source',
]
BASE_WEBSITE = 'https://www.flightstats.com/v2/flight-tracker/arrivals'

INPUT_FILE_NAME = 'raw_airports.csv'
OUTPUT_FILE_NAME = 'raw_arrivals.csv'


def main():
    tmr = dt.date.today() + dt.timedelta(days=1)
    print(f'Scrapping data for the date: {tmr}')

    airport_code_list = get_airport_code_list('ICAO', 'Ecuador')
    print(f'Airport International Code list: {airport_code_list}')

    # Range of time to search for arrivals. i.e. Search arrivals between 0-6 hour
    valid_hours = [0, 6, 12, 18]

    flights = []
    # airport_code_list = ['SECO']  # For testing
    for airport_code in airport_code_list:
        for hour in valid_hours:
            flights += scrap_flight_stats(airport_code, tmr.year, tmr.month, tmr.day, hour)

    # Imports list of dictionary and flattens data
    df = json_normalize(flights)

    # Replace '.' with '_' for in column names
    df.rename(lambda x: x.replace('.', '_'), inplace=True, axis=1)

    create_dir(OUTPUT_DIR, to_clear=False)

    output_file_path_1: str = os.path.join(DBT_DATA_DIR, OUTPUT_FILE_NAME)
    output_file_path_2: str = os.path.join(OUTPUT_DIR, OUTPUT_FILE_NAME)

    print(f'Saving data to {output_file_path_1}')
    df.to_csv(path_or_buf=output_file_path_1, index=False)

    print(f'Saving data to {output_file_path_2}')
    df.to_csv(path_or_buf=output_file_path_2, index=False)

    print('Sample Results:')
    print(df)

    print('Done')


def get_airport_code_list(iata_or_icao='ICAO', country='Ecuador'):
    """Gets the list of Airport Codes (IATA or ICAO) from the CSV file"""
    df = pd.read_csv(
        os.path.join(OUTPUT_DIR, INPUT_FILE_NAME),
        index_col='Airport_ID'
    ).replace('"', '', regex=True)

    airport_code_df = df[df['Country'] == country][iata_or_icao]

    return airport_code_df.tolist()


def scrap_flight_stats(airport_code, year, month, date, hour):
    """Web scrapper for Airport Arrivals from www.flightstats.com"""
    full_url = f'{BASE_WEBSITE}/{airport_code}/?year={year}&month={month}&date={date}&hour={hour}'

    response = requests.get(full_url)
    source = response.text

    print(f'Getting for Airport Code: {airport_code} | For hour: {hour} | {full_url}')

    # Use REGEX to find the JSON data that is available in the website source code.
    match = re.search(r'(__NEXT_DATA__\s+?=\s+?)(.*)(\s+?module={})', source)
    raw_data = match.group(2)

    # Use the JSON parser to parse the str
    json_data = json.loads(raw_data)

    # Extract the proper fields in the JSON
    flight_tracker = json_data['props']['initialState']['flightTracker']
    flights = flight_tracker['route']['flights']

    # Add back arrival airport information for joins purposes.
    for flight in flights:
        flight['date'] = flight_tracker['route']['header']['date']
        flight['iata'] = flight_tracker['route']['header']['arrivalAirport']['iata']
        flight['icao'] = flight_tracker['route']['header']['arrivalAirport']['icao']
        flight['airport_name'] = flight_tracker['route']['header']['arrivalAirport']['name']

    print(f'Number of results for {airport_code}: {len(flights)}')

    return flights

if __name__ == '__main__':
    main()
