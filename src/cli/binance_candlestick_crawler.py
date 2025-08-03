import click

from src.artifacts.binance_supported_pairs import pairs
from src.constants.binance_constants import BINANCE_INTERVALS
from src.databases.mongodb import MongoDB
from src.jobs.crawl_binance_candlesticks_realtime_job import CrawlBinanceCandlesticksRealtimeJob
from src.utils.logger_utils import get_logger

logger = get_logger('Binance Candlesticks Realtime Crawler')


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-o', '--output_db', default=None, type=str, help='Output Mongodb Connection String')
@click.option('-c', '--coin', default=None, type=str, help='Coin')
@click.option('-t', '--time-interval', default=None, type=int, help='Time interval by seconds')
def binance_candlestick_crawler(
        output_db, coin, time_interval
):
    if time_interval not in BINANCE_INTERVALS.values():
        raise f"Time Interval {time_interval} not supported"
    if f'{coin.upper()}USDT' not in pairs:
        raise "Coin not supported"

    logger.info(f'Start Crawl Candlestick')
    logger.info(f'Processing coin: {coin}')
    last_sync_file = f'.data/last_crawl_binance_candlesticks_realtime_{coin}_{time_interval}.txt'

    item_exporter = MongoDB(connection_url=output_db)

    scheduler = f'^true@{time_interval}'

    job = CrawlBinanceCandlesticksRealtimeJob(
        item_exporter=item_exporter,
        coin=coin,
        candle_interval=get_binance_interval_str(time_interval),
        scheduler=scheduler,
        last_sync_file=last_sync_file
    )
    job.run()


def get_binance_interval_str(seconds: int) -> str:
    for k, v in BINANCE_INTERVALS.items():
        if v == seconds:
            return k
