import psycopg2
import sys
sys.path.append('/home/proj/price_keeper')
from price_keeper import TokenInfoDB
import json

db = TokenInfoDB()

decimal_map = {t[0]: t[1] for t in db.get_all_decimal()}

with open('utils/decimal/token_decimal.json', 'w') as f:
    f.write(json.dumps(decimal_map))

