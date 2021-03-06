import datetime
import os
curPath = os.path.abspath(os.path.dirname(__file__))
import sys
sys.path.append(curPath[:-4])
from base_token import BaseToken

if __name__ == "__main__":
    token = BaseToken(contract_address='0x187eff9690e1f1a61d578c7c492296eaab82701a')
    status, price, time = token.get_price_until()
    print('status =', status, 'price =', price, 'time =', time)
    status, price, time = token.get_price_until(time=datetime.datetime(2021, 5, 21, 12, 0, 0))
    print('status =', status, 'price =', price, 'time =', time)
    print(token.get_name())
    print(token.get_symbol())
    print(token.get_decimal())
    
    
    # MKR
    # token_mkr = BaseToken(contract_address='0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2')
    # print(token_mkr.get_name())

    # ERC-721 Token 
    # token_erc721 = BaseToken(contract_address='0xc0cf5b82ae2352303b2ea02c3be88e23f2594171')
    # print(token_erc721.get_decimal())

