import datetime
from re import S
from loguru import logger
from web3 import Web3, exceptions
from settings import WEB3_HTTP_URL, ERC20_ABI
from token_db import TokenInfoDB, TokenPriceDB
import json
    
class BaseToken:

    w3 = Web3(Web3.HTTPProvider(WEB3_HTTP_URL, request_kwargs={'timeout': 6000}))
    with open(ERC20_ABI) as f:
        erc20_abi = json.load(f)
    info_db = TokenInfoDB()
    price_db = TokenPriceDB()
    def __init__(self, contract_address, name=None,
                symbol=None, type=None, decimal=None, 
                price=None, price_time=None, tvl=None, total_supply=None, 
                uri=None, api_tag=None, ex_tag=None):
        self.contract_address = contract_address
        self.name = name
        self.symbol = symbol
        self.decimal = decimal
        self.type = type
        self.price = price  # Latest price
        self.price_time = price_time    # price update time
        self.tvl = tvl
        self.total_supply = total_supply
        self.uri = uri
        self.api_tag = api_tag
        self.ex_tag = ex_tag
        self.w3_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(self.contract_address), abi=self.erc20_abi)
           
    def get_name(self):

        try:
            # 先通过info_db查找
            if self.name is not None:
                return self.name
            else:
                name = self.info_db.get_name_by_address(self.contract_address)
                if name is None:
                    # 如果不存在, 再通过web3查找
                    name =  self.w3_contract.functions.name().call()
                self.name = name
                return name
        except OverflowError as e:
            # TODO MKR
            logger.warning(f"Token {self.name} Address{self.contract_address}: Name over flow.")
            return None
        except Exception as e:
            logger.warning(f"Token {self.name} Address{self.contract_address}: Something wrong when get name info from node.")
            return None

    def get_symbol(self):

        try:
            # 先通过info_db查找
            if self.symbol is not None:
                return self.symbol
            else:
                symbol = self.info_db.get_symbol_by_address(self.contract_address)
                if symbol is None:
                    # 如果不存在, 再通过web3查找
                    symbol =  self.w3_contract.functions.symbol().call()
                self.symbol = symbol
                return symbol

        except Exception as e:
            logger.warning(f"Token {self.name} Address{self.contract_address}: Something wrong when get symbol info from node.")

    def get_decimal(self):

        try:
            # 先通过info_db查找
            if self.decimal is not None:
                return self.decimal
            else:
                dec = self.info_db.get_decimal_by_address(self.contract_address)
                if dec is None:
                    # 如果不存在, 再通过web3查找
                    self.decimal = self.w3_contract.functions.decimals().call()
                else:
                    self.decimal = dec = dec[0] 
                return self.decimal
                
        except exceptions.ContractLogicError as e:
            self.type = 'ERC-721'
            logger.warning(f"Token {self.name} Address{self.contract_address}: Has no decimal function, maybe ERC721 token.")
            return None
        except Exception as e:
            logger.warning(f"Token {self.name} Address{self.contract_address}: Something wrong when get decimals info from node")
            return None

    def get_price_until(self, time=None):
        """ Get the latest price until a given time. """
        
        if time is None:
            time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

        res = self.price_db.get_price(self.contract_address, time)

        if res:
            return res[0]
        else:
            return 'Failed', None, time

    def get_prices_until(self, time=None, limit=5):
        """ Get whole price list until a given time. """

        if time is None:
            time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

        res = self.price_db.get_whole_price(self.contract_address, time, limit=limit)
        
        if res:
            return res
        else:
            return 'Failed', None, time

if __name__ == "__main__":
    tk = BaseToken(contract_address='0x6b3595068778dd592e39a122f4f5a5cf09c90fe2')
    print(tk.get_decimal())
    print(tk.get_name())
    print(tk.get_symbol())

    