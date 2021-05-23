from web3._utils.filters import select_filter_method
from loguru import logger
from typing import List
from pycoingecko.api import CoinGeckoAPI
from base_token import BaseToken
import time
import requests
import random

class TokenApi(object):

    def __init__(self, api=None, api_tag=None, ex_tag=None, base_url=None):
        self.api = api
        self.api_tag = api_tag
        self.ex_tag = ex_tag
        self.base_url = base_url
        self.token_list = []    
    
    def get_token_list(self):
        pass

    def get_token_price(self):
        pass

class APICoinGecko(TokenApi):

    def __init__(self, api_tag='CoinGecko', ex_tag=None):
        super().__init__(api_tag=api_tag, ex_tag=ex_tag)

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
        # tmp_token_list = [tk for tk in tmp_token_list if "ethereum" in tk["platforms"] and tk["platforms"]["ethereum"] != ""]
        valid_token_list = []
        for token in __token_list:
            address = None
            if "ethereum" in token["platforms"] and token["platforms"]["ethereum"] != "":
                address = token["platforms"]["ethereum"]
            if address is None:
                continue
            valid_token_list.append(token)
        valid_token_addresses = [token["platforms"]["ethereum"] for token in valid_token_list]
        # prices = self.api.get_token_price(id='ethereum', contract_addresses=address_list, vs_currencies='usd')
        start = 0
        step = 100
        prices = dict()
        while start + step < len(valid_token_list):
            try:
                prices.update(self.api.get_token_price(id='ethereum', contract_addresses=valid_token_addresses[start:start+step],
                         vs_currencies='usd'))
                start += step
            except requests.exceptions.HTTPError as e:
                if e == "429 Client Error":
                    logger.info("Too many request for url.")
                    time.sleep(random.randint(1, 3))
            
        for token in valid_token_list:        
            address = token["platforms"]["ethereum"]
            # some address may not exists in prices and prices[address] maybe empty {}
            if address in prices and prices[address] and prices[address]['usd']:
                base_token = BaseToken(contract_address=address, name=token['name'], symbol=token['symbol'], 
                                        price=prices[address]['usd'], api_tag=self.api_tag)
                if base_token.get_decimal() is not None:
                    base_token.type = 'ERC-20'
                else:
                    base_token.type = 'ERC-721'
                logger.info(f'Successful add token {base_token.name}')
                self.token_list.append(base_token)
        
        return self.token_list

class ApiPool:

    def __init__(self):
        self.api_pool : List[TokenApi] = []

    def get_api_list(self):
        if self.api_pool is not None:
            return self.api_pool

    def add_api(self, api : TokenApi):
        self.api_pool.append(api)    
        
if __name__ == "__main__":
    ac = APICoinGecko()
    ac.api = CoinGeckoAPI()
    api_pool = ApiPool()
    api_pool.add_api(ac)
    # print(len(api_pool.get_api_list()))
    for t in api_pool.get_api_list():
        t.get_token_list()
        # for tk in t.get_token_list():
        #     print(tk)
            # print(tk.name)
        # print(isinstance(t, APICoinGecko))
        # print(t.get_coins_list())