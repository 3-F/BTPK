PGSQL_DB = "defi"
PGSQL_HOST = "192.168.3.2"
PGSQL_PORT = 5432
PGSQL_USER = "junjie"
PGSQL_PASSWORD = "123123"

# INFURA_PROJ_ID = '709b8fafa0ec43b0af9fdc3cf43dd13a'
# WEB3_HTTP_URL = f"https://mainnet.infura.io/v3/{INFURA_PROJ_ID}"

WEB3_HTTP_URL = f"http://192.168.3.2:8546"

import os
curPath = os.path.abspath(os.path.dirname(__file__))

ERC20_ABI = f'{curPath}/utils/abi/erc20_abi.json'
