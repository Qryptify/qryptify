import click

from src.cli.binance_price_realtime_crawler import binance_price_realtime_crawler


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    # Command line
    pass


cli.add_command(binance_price_realtime_crawler, "binance_price_realtime_crawler")
