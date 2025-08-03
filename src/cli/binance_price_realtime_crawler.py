import click

from src.artifacts.binance_supported_pairs import pairs
from src.databases.mongodb import MongoDB
from src.jobs.crawl_binance_price_realtime_job import CrawlBinancePriceRealtimeJob
from src.utils.logger_utils import get_logger

logger = get_logger('Binance Price Realtime Crawler')


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-o', '--output_db', default=None, type=str, help='Output Mongodb Connection String')
@click.option('-c', '--coin', default=None, type=str, help='Coin')
def binance_price_realtime_crawler(
        output_db, coin
):
    if f'{coin.upper()}USDT' not in pairs:
        raise "Coin not supported"

    logger.info(f'Start Crawl ')
    logger.info(f'Processing coin: {coin}')
    last_sync_file = f'.data/last_crawl_binance_price_realtime_{coin}.txt'

    item_exporter = MongoDB(connection_url=output_db)

    job = CrawlBinancePriceRealtimeJob(
        item_exporter=item_exporter,
        coin=coin,
        last_sync_file=last_sync_file
    )
    job.run()
