import csv
import re
from os import path
import requests

from utils.tools import create_dir


PARENT_PATH: str = path.dirname(__file__)
ROOT_PATH: str = path.abspath(path.join(PARENT_PATH, '..'))
DBT_DATA_DIR: str = path.join(ROOT_PATH, 'dbt/data')
OUTPUT_DIR: str = path.join(PARENT_PATH, 'output')

AIRPORT_WEBSITE = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat'
OUTPUT_FILE_NAME = 'raw_airports.csv'
HEADERS = [
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


def main():
    print(f'Downloading raw airport data from {AIRPORT_WEBSITE}.')
    response = requests.get(AIRPORT_WEBSITE)

    create_dir(OUTPUT_DIR)

    output_file_path_1 = path.join(DBT_DATA_DIR, OUTPUT_FILE_NAME)
    output_file_path_2 = path.join(OUTPUT_DIR, OUTPUT_FILE_NAME)

    output_csv(headers=HEADERS, response=response, file_path=output_file_path_1)
    output_csv(headers=HEADERS, response=response, file_path=output_file_path_2)

    print(response.text)
    print('Done')


def output_csv(headers, response, file_path):
    print(f'Saving data to `{path.abspath(file_path)}`.')
    with open(file_path, 'w') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for line in response.iter_lines(decode_unicode=True):
            # REGEX Source: https://stackoverflow.com/questions/18893390/splitting-on-comma-outside-quotes
            w.writerow(re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", line))


if __name__ == '__main__':
    main()
