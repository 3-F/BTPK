from os import times
import settings
from web3._utils.filters import select_filter_method
from loguru import logger
from typing import List
from pycoingecko.api import CoinGeckoAPI
from base_token import BaseToken
import time
import requests
import random
import json

class TokenApi(object):
    
    with open(settings.DECIMAL) as f:
        decimal_map = json.load(f)
    def __init__(self, api=None, api_tag=None, ex_tag=None, base_url=None):
        self.api = api
        self.api_tag = api_tag
        self.ex_tag = ex_tag
        self.base_url = base_url
        self.token_list = []
        self.token_map = {}    
    
    def get_token_list(self):
        pass

    def get_token_price(self):
        pass

    def refresh_token_list(self):
        pass

    def get_token(self, address=None):
        if address is None:
            logger.info("Please input an valid address.")
            return None
        if not self.token_map[address]:
            logger.info(f"[API] {self.api_tag} has no token in address {address}")
        else:
            return self.token_map[address]

class APICoinGecko(TokenApi):

    def __init__(self, api_tag='CoinGecko', ex_tag=None):
        self.id_to_address = {}
        self.valid_token_ids = []
        super().__init__(api=CoinGeckoAPI(), api_tag=api_tag, ex_tag=ex_tag)

    def get_token_list(self, retry_times=5) -> List[BaseToken]:

        if self.token_list:
            return self.token_list

        while retry_times > 0:
            try:
                __token_list = self.api.get_coins_list(include_platform=True)
                break
            except requests.exceptions.HTTPError as e:
                time.sleep(random.randint(50, 200))
                retry_times -= 1
                logger.info(f"Too Many Requests for api:{self.api_tag}. Retry {retry_times} times.")
            except requests.exceptions.ConnectionError as e:
                logger.info("Connect aborted.")


        for token in __token_list:
            address = None
            if "ethereum" in token["platforms"] and token["platforms"]["ethereum"] != "":
                address = token["platforms"]["ethereum"]
            if address is None:
                continue
            base_token = BaseToken(contract_address=address, name=token['name'], symbol=token['symbol'], api_tag=self.api_tag)
            if address in self.decimal_map:
                base_token.decimal = self.decimal_map[address]
                base_token.type = 'ERC-20'
            # else:
            #     decimal = base_token.get_decimal()
            #     self.decimal_map[address] = decimal

            self.token_list.append(base_token)
            self.valid_token_ids.append(token["id"])
            self.id_to_address[token["id"]] = address
            self.token_map[address] = base_token
            # logger.info(f'Successfully add token {base_token.name}')

        self.refresh_token_list()

        return self.token_list

    def refresh_token_list(self):
        
        start = 0
        step = 300
        while start + step < len(self.valid_token_ids):
            try:
                prices_info = self.api.get_price(ids=self.valid_token_ids[start:start+step], vs_currencies='usd',
                            include_market_cap=False, include_last_updated_at=True)
                if not self.token_list:
                    logger.info('Token list is empty, could not refresh it.')
                for id in prices_info.keys():
                    if 'usd' not in prices_info[id] or not prices_info[id]['usd']:
                        continue
                    token = self.token_map[self.id_to_address[id]]
                    last_update = token.price_time
                    timestamp = prices_info[id]['last_updated_at']
                    this_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                    if last_update is None or this_update > last_update:
                        token.price_time = this_update
                        token.price = prices_info[id]['usd']
                start += step
            except requests.exceptions.HTTPError as e:
                if e == "429 Client Error":
                    logger.info("Too many request for url.")
                    time.sleep(random.randint(1, 3))

class ApiPool:

    def __init__(self):
        self.api_pool : List[TokenApi] = []

    def get_api_list(self):
        if self.api_pool is not None:
            return self.api_pool

    def add_api(self, api : TokenApi):
        api.get_token_list()
        self.api_pool.append(api)    
        
if __name__ == "__main__":
    ac = APICoinGecko()
    api_pool = ApiPool()
    api_pool.add_api(ac)
    # print(len(api_pool.get_api_list()))
    for t in api_pool.get_api_list():
        t.get_token_list()
        
        start = time.time()
        t.refresh_token_list()
        end = time.time()
        logger.info(f"time spend: {end-start}s")

        start = time.time()
        t.refresh_token_list()
        end = time.time()
        logger.info(f"time spend: {end-start}s")
        # for tk in t.get_token_list():
        #     print(tk)
            # print(tk.name)
        # print(isinstance(t, APICoinGecko))
        # print(t.get_coins_list())