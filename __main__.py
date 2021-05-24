import psycopg2
from price_keeper import PriceKeeper
from api_keeper import ApiPool, TokenApi, APICoinGecko, CoinGeckoAPI
import sys
import os 
from loguru import logger
from token_db import TokenInfoDB, TokenPriceDB
import schedule
from threading import Thread
from time import time

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)

def _on_exit():
    logger.info("结束进程，后续处理中...")
    sys.exit(0)

def _main(args=None):
    """ Fetch price and info of tokens, and write into database.
    """    
    
    # Instancce price_keeper
    price_keeper = PriceKeeper()
    price_keeper.info_db = TokenInfoDB()
    price_keeper.price_db = TokenPriceDB()

    # Instancce APIs (Now only have CoinGecko API)
    coin_gecko_api = APICoinGecko()
    
    # Instance ApiPool
    price_keeper.api_pool = ApiPool()
    # Add customize api into api_pool
    price_keeper.api_pool.add_api(coin_gecko_api)
    
    price_keeper.info_db.create_table()
    price_keeper.price_db.create_table()
    logger.info('Start to sync tables.')
    # price_keeper.refresh_info()
    # price_keeper.refresh_price()
    schedule.every().day.at("01:00").do(price_keeper.refresh_info)
    schedule.every(10).minutes.do(price_keeper.refresh_price)

    while True:
        schedule.run_pending()

# schedule.run_pending
    
if __name__ == "__main__":
    sys.exit(_main())