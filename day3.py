import os

import pandas as pd
from google.oauth2 import service_account
from sqlalchemy import create_engine

from day1 import KEYFILE

KEYFILE = 'ensai-2025-8f3e0d316c90.json'

def get_postgres_engine():
    username = "postgres"
    password = os.getenv("PG_PASSWORD")
    host = os.getenv("PG_HOST")
    database = "app"
    return create_engine(f"postgresql://{username}:{password}@{host}/{database}", echo=False)

def get_biquery_credentials():
    return service_account.Credentials.from_service_account_file(KEYFILE)

def get_data_from_postgres(table: str, limit="10") -> pd.DataFrame:
    engine = get_postgres_engine()
    limit = f"LIMIT {limit}" if limit else ""
    return pd.read_sql(f"SELECT * FROM {table} {limit}", con=engine)

def save_data_to_bigquery(table: str, data: pd.DataFrame) -> None:
    credentials = get_biquery_credentials()
    fqdn_name = f"raw_christophe.{table}"
    data.to_gbq(fqdn_name, credentials=credentials, project_id="ensai-2025", if_exists="replace")

def transfer_data(table: str):
    df = get_data_from_postgres(table)
    save_data_to_bigquery(table, df)


def run():
    transfer_data('prenoms')

if __name__ == '__main__':
    run()