import click

@click.command()
@click.argument('date')
def run(date):
    """Run the CLI to scrape hacker news for a given date."""
    click.echo('Scraping Hacker News for date: {}'.format(date))

if __name__ == '__main__':
    run()