from base_token import BaseToken
from loguru import logger
from web3._utils.filters import select_filter_method
from token_db import TokenInfoDB
from api_keeper import ApiPool, APICoinGecko
from pycoingecko import CoinGeckoAPI
import json
import requests
import logging
from settings import WEB3_HTTP_URL, ERC20_ABI
import datetime

class PriceKeeper:
    def __init__(self):
        self.info_db = None
        self.price_db = None
        self.api_pool = None
        self.tokens = []
        
    def refresh_info(self):
        """ Update token_info table """
        
        logger.info(f"[Table] token_info is updating data...")
        apis = self.api_pool.get_api_list()
        for api in apis:
            # TODO it need almost 1 min to update all data
            self.tokens = api.get_token_list()
            token_exists = self.info_db.get_address_list()   
            # 先查数据库token_info，看是否已经记录address
            for token in self.tokens:
                # addr = self.info_db.get_address_by_name(coin['name'])
                if token_exists is not None and token.contract_address in token_exists:
                    continue
                else:
                    self.info_db.insert(self.token_info(token))
                    logger.info(f'[INSERT]Table:token_info Token:{token.name} Address:{token.contract_address}')
    
    def refresh_price(self):
        """ Update token_price table """
        
        logger.info(f"[Table] token_price is updating data...")
        apis = self.api_pool.get_api_list()
        for api in apis:
            # TODO it need almost 1 min to update all data
            self.tokens = api.get_token_list()
            for token in self.tokens:
                self.price_db.insert(self.token_price(token))
                logger.info(f'[INSERT]Table:token_price Token:{token.name} Address:{token.contract_address}')
        
    def token_info(self, token : BaseToken):
        """生成可以insert到token_info表中的value元组"""

        # fields = ['address', 'created_time', 'name', 'symbol', 'decimal', 'type', 'uri']
        return (token.contract_address, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'),
                token.name, token.symbol, token.decimal, token.type, token.uri)

    def token_price(self, token : BaseToken):
        """生成可以insert到token_price表中的value元组"""

        # fields = ['address', 'price', 'time', 'status', 'tvl', 'total_supply',  'origin']
        status = 'Unknown'
        price = token.price
        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        if price is not None:
            status = 'Active'
        return (token.contract_address, price, time, status, token.tvl, token.total_supply,  token.api_tag, token.ex_tag)

if __name__ == "__main__":
    ck = PriceKeeper()
    ac = APICoinGecko()
    ac.api = CoinGeckoAPI()
    ck.api_pool = ApiPool()
    ck.api_pool.add_api(ac)
    ck.info_db = TokenInfoDB()
    ck.refresh_info()
    
    # ck.refresh_price()
    # print(len(api_pool.get_api_list()))
    # for t in api_pool.get_api_list():
    #     for tk in t.get_token_list():
    #         print(tk)
    