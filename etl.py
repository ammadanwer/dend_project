import configparser
import os

import d6tstack

import boto3
import pandas as pd

POVERTY_FILE_NAME = 'PovertyEstimates.xls'
POVERTY_SHEET_NAME = 'Poverty Data 2017'
UNEMPLOYMENT_FILE_NAME = 'Unemployment.xls'
UNEMPLOYMENT_SHEET_NAME = 'Unemployment Med HH Inc'

config = configparser.ConfigParser()
config.read('credentials.cfg')
os.environ['AWS_ACCESS_KEY_ID'] = config.get('AWS_KEYS', 'AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = config.get('AWS_KEYS', 'AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = config.get('AWS_KEYS', 'AWS_BUCKET_NAME')


def get_uri():
    host = config.get('POSTGRES_CREDENTIALS', 'HOST')
    port = config.get('POSTGRES_CREDENTIALS', 'PORT')
    database = config.get('POSTGRES_CREDENTIALS', 'DATABASE')
    user = config.get('POSTGRES_CREDENTIALS', 'USERNAME')
    password = config.get('POSTGRES_CREDENTIALS', 'PASSWORD')
    uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    return uri


def load_population_file(s3_client):
    obj = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=POVERTY_FILE_NAME)
    df = pd.read_excel(obj['Body'], sheet_name=POVERTY_SHEET_NAME, header=3, index=0)

    dim_county_df = df[['FIPStxt', 'Area_Name', 'State']]
    dim_county_df.rename(columns={'FIPStxt': 'fips_id', 'Area_Name': 'name', 'State': 'state'}, inplace=True)
    print(dim_county_df.columns)
    print(dim_county_df.head())
    uri = get_uri()
    print('Populating dim_county!')
    d6tstack.utils.pd_to_psql(dim_county_df, uri, 'dim_county', if_exists='replace')

    fact_poverty_df = df[['FIPStxt', 'PCTPOVALL_2017']]
    fact_poverty_df.rename(columns={'FIPStxt': 'fips_id', 'PCTPOVALL_2017': 'percentage'}, inplace=True)
    fact_poverty_df['year'] = 2017
    print(fact_poverty_df.columns)
    print(fact_poverty_df.head())
    print('Populating fact_poverty!')
    d6tstack.utils.pd_to_psql(fact_poverty_df, uri, 'fact_poverty', if_exists='replace')


def load_unemployement_file(s3_client):
    obj = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=UNEMPLOYMENT_FILE_NAME)

    df = pd.read_excel(obj['Body'], sheet_name=UNEMPLOYMENT_SHEET_NAME, header=7, index=0)
    fact_unemployment_df = df[['FIPS', 'Unemployment_rate_2017']]
    fact_unemployment_df.rename(columns={'FIPS': 'fips_id', 'Unemployment_rate_2017': 'percentage'}, inplace=True)
    fact_unemployment_df['year'] = 2017

    print(fact_unemployment_df.columns)
    print(fact_unemployment_df.head())
    print('Populating fact_unemployment!')

    uri = get_uri()
    d6tstack.utils.pd_to_psql(fact_unemployment_df, uri, 'fact_unemployment', if_exists='replace')


def main():
    """
    The main function responsible for loading of data from xls to pandas to postgres
    """
    s3_client = boto3.client('s3')
    load_population_file(s3_client)
    load_unemployement_file(s3_client)


if __name__ == "__main__":
    main()
