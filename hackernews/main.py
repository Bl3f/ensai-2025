import os
import time
from email.policy import default

from google.oauth2 import service_account
from google.cloud import bigquery
from scrape import extract_all_links

import click
import requests

import pandas as pd

KEYFILE = '../ensai-2025-8f3e0d316c90.json'

def get_biquery_credentials():
    return service_account.Credentials.from_service_account_file(KEYFILE)

def create_table(name, client):
    schema = [
        bigquery.SchemaField("rank", "INTEGER"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("points", "INTEGER"),
        bigquery.SchemaField("author", "STRING"),
        bigquery.SchemaField("created_at", "STRING"),
        bigquery.SchemaField("comments", "INTEGER"),
        bigquery.SchemaField("partition_date", "DATE"),

    ]

    table = bigquery.Table(name, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="partition_date",
    )

    client.create_table(table, exists_ok=True)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('date', type=click.DateTime(['%Y-%m-%d']))
@click.option("--pages", default=5, help="Number of pages to scrape.")
@click.option("--scrape/--no-scrape", is_flag=True, help="Scrape the data.", default=True)
@click.option('--sleep', type=int, default=1, help='Sleep time between requests.')
def ingest(date, pages, scrape, sleep):
    """Run the CLI to scrape hacker news for a given date."""
    date_str = date.strftime('%Y-%m-%d')
    filename = f"hackernews.{date_str}.csv"

    if scrape:
        click.echo(f'Scraping Hacker News for date: {date_str}')

        results = []
        for i in range(pages):
            url = f"https://news.ycombinator.com/front?day={date_str}&p={i+1}"
            click.echo(f"Getting page {i+1} for date {date_str}...")
            response = requests.get(url)
            results.extend(extract_all_links(response.text, date))
            time.sleep(sleep)

        df = pd.DataFrame(results)
        df.to_csv(f"hackernews.{date_str}.csv", index=False)

    df = pd.read_csv(filename, parse_dates=["partition_date"])
    df["partition_date"] = df["partition_date"].dt.date

    credentials = get_biquery_credentials()
    client = bigquery.Client(credentials=credentials)
    table_name = "ensai-2025.christophe.hackernews"
    create_table(table_name, client)

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        time_partitioning=bigquery.table.TimePartitioning(type_="DAY", field="partition_date"),
    )

    # Include target partition in the table id:
    table_id = f"{table_name}${date.strftime('%Y%m%d')}"
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)  # Make an API request
    job.result()

@cli.command()
@click.argument('file', type=click.Path(exists=True))
def news(file):
    df = pd.read_parquet(file)

    for index, row in df.iterrows():
        url = row["url"]
        partition_date = row["partition_date"]
        rank = row["rank"]
        try:
            folder = os.path.join("pages", partition_date)
            filename = os.path.join(folder, f"{rank}.html")

            if os.path.exists(filename):
                click.echo(f"Skipping {url} as it already exists.")
                continue

            if not os.path.exists(folder):
                os.makedirs(folder)

            click.echo(f"Downloading {url}...")
            response = requests.get(url, timeout=5)
            with open(filename, "w") as f:
                f.write(response.text)
        except Exception as e:
            click.echo(f"Failed to download {url}: {e}")
            continue


if __name__ == '__main__':
    cli()