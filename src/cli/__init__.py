import click

from src.cli.binance_price_realtime_crawler import binance_price_realtime_crawler
from src.cli.binance_candlestick_crawler import binance_candlestick_crawler


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    # Command line
    pass


cli.add_command(binance_price_realtime_crawler, "binance_price_realtime_crawler")
cli.add_command(binance_candlestick_crawler, "binance_candlestick_crawler")
