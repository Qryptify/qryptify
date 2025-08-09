import click
from loguru import logger

from qryptify.artifacts.binance_supported_pairs import pairs
from qryptify.constants.binance_constants import BINANCE_INTERVALS
from qryptify.databases.timescaledb import TimescaleDB


def get_binance_interval_str(seconds: int) -> str:
    for k, v in BINANCE_INTERVALS.items():
        if v == seconds:
            return k
    raise ValueError(f"Interval for {seconds} seconds not found.")


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-o',
              '--output_db',
              default=None,
              type=str,
              help='Output TimescaleDB Connection String')
@click.option('-c', '--coin', default=None, type=str, help='Coin')
@click.option('-t',
              '--time-interval',
              default=None,
              type=int,
              help='Time interval by seconds')
@click.option('--fetch-limit',
              default=15,
              type=int,
              help='Number of recent candles to fetch and insert (for testing)'
              )
def binance_candlestick_crawler(output_db, coin, time_interval, fetch_limit):
    if time_interval not in BINANCE_INTERVALS.values():
        raise ValueError(f"Time Interval {time_interval} not supported")
    # Accept both BTC and BTCUSDT
    symbol = coin.upper()
    if not symbol.endswith('USDT'):
        symbol = symbol + 'USDT'
    if symbol not in pairs:
        raise ValueError("Coin not supported")

    logger.info(f'Start Crawl Candlestick')
    logger.info(f'Processing coin: {symbol}')
    # For testing: fetch recent candles and insert, then exit
    import requests
    item_exporter = TimescaleDB(connection_url=output_db)
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {
        'symbol': symbol,
        'interval': get_binance_interval_str(time_interval),
        'limit': fetch_limit
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    candles = response.json()
    count = 0
    for candle in candles:
        kline = {
            "timestamp": int(candle[0] // 1000),
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "close_time": int(candle[6] // 1000),
            "quote_asset_volume": float(candle[7]),
            "number_of_trades": int(candle[8]),
            "taker_buy_base": float(candle[9]),
            "taker_buy_quote": float(candle[10]),
            "symbol": symbol,
            "interval": get_binance_interval_str(time_interval)
        }
        item_exporter.insert_realtime_candle(kline)
        count += 1
    print(
        f"Inserted {count} candles for {symbol} at interval {time_interval}s.")


if __name__ == "__main__":
    import click
    click.echo("Starting Binance Candlestick Crawler...")
    binance_candlestick_crawler()
