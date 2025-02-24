import os

import pandas as pd
from google.oauth2 import service_account
from sqlalchemy import create_engine

from day1 import KEYFILE

KEYFILE = 'ensai-2025-8f3e0d316c90.json'
RAW_DATASET_NAME = 'raw_christophe'

def get_postgres_engine():
    username = "postgres"
    password = os.getenv("PG_PASSWORD")
    host = os.getenv("PG_HOST")
    database = "app"
    return create_engine(f"postgresql://{username}:{password}@{host}/{database}", echo=False)

def get_biquery_credentials():
    return service_account.Credentials.from_service_account_file(KEYFILE)

def get_data_from_postgres(table: str, limit="10", ingestion_mode="full", partition_col=None) -> pd.DataFrame:
    engine = get_postgres_engine()
    limit = f"LIMIT {limit}" if limit else ""
    if ingestion_mode == 'full':
        return pd.read_sql(f"SELECT * FROM {table} {limit}", con=engine)
    elif ingestion_mode == 'incremental':
        partition = "2020"
        return pd.read_sql(f"SELECT * FROM {table} WHERE {partition_col} = '{partition}' {limit}", con=engine)

def get_data_from_url(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

def save_data_to_bigquery(table: str, data: pd.DataFrame) -> None:
    credentials = get_biquery_credentials()
    fqdn_name = f"{RAW_DATASET_NAME}.{table}"
    data.to_gbq(
        fqdn_name,
        credentials=credentials,
        project_id="ensai-2025",
        if_exists="replace",
        location="EU",
    )

def transfer_data(config: dict) -> None:
    if config['type'] == 'postgres':
        df = get_data_from_postgres(config['table'], config.get('limit'), config.get('ingestion_mode'), config.get('partition_col'))

    if config["type"] == 'url':
        df = get_data_from_url(config["url"])

    save_data_to_bigquery(config['table'], df)


def run():
    configs = [
        {'table': 'prenoms', 'limit': '10', 'type': 'postgres', 'ingestion_mode': 'incremental', 'partition_col': 'annais'},
        {'table': 'regions', 'type': 'url', 'url': 'https://www.data.gouv.fr/fr/datasets/r/70cef74f-70b1-495a-8500-c089229c0254'},
    ]

    for config in configs:
        print(f"Transferring data for {config['table']} (type: {config['type']})...")
        transfer_data(config)
        print("Done.")

if __name__ == '__main__':
    run()