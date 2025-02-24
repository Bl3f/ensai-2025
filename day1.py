from google.cloud import storage
from datetime import datetime, timedelta
import pandas as pd
import pandas_gbq
from sqlalchemy import create_engine
from google.oauth2 import service_account


KEYFILE = 'ensai-2025-8f3e0d316c90.json'

def ex_1_bucket():
    # Instantiates a client
    client = storage.Client.from_service_account_json(KEYFILE)

    # The name for the new bucket
    bucket_name = "christophe-dates"

    # Creates the new bucket
    if not client.bucket(bucket_name).exists():
        bucket = client.create_bucket(bucket_name, location="EU")
        print(f"Bucket {bucket.name} created.")
    else:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket {bucket_name} already exists.")

    start = datetime(2025, 1, 1)
    while start < datetime(2026, 1, 1):
        blob = bucket.blob(f'{start.strftime("%Y-%m-%d")}/')
        blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')

        start += timedelta(days=1)

def ex_4_nyc_sql():
    host = ""
    username = "postgres"
    password = ""

    df = pd.read_parquet("yellow_tripdata_2024-07.parquet")
    engine = create_engine(f"postgresql://{username}:{password}@{host}", echo=False)
    df[:1000].to_sql("taxi", con=engine, if_exists="replace")


def copy_data():
    credentials = service_account.Credentials.from_service_account_file(KEYFILE)
    prenoms = pandas_gbq.read_gbq("SELECT * FROM ml.prenoms", project_id="ensai-2025", credentials=credentials)

    print(prenoms.head())

    password = "/I>x=r6_(<H8kaQ`"
    engine = create_engine(f'postgresql://postgres:{password}@35.205.48.250:5432/app', echo=False)
    prenoms.to_sql('prenoms', con=engine, if_exists='replace', index=False)


if __name__ == "__main__":
    copy_data()
