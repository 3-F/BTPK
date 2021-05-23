from logging import log
import settings
from psycopg2 import connect
import psycopg2
from loguru import logger

# class Singleton(type):
#     __instances = {}
#     def __call__(cls, *args, **kwds):
#         if cls not in cls.__instances:
#             cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
#         return cls.__instances[cls]

# class TokenDB(object, metaclass=Singleton):

#     def __init__(self, dbname=settings.PGSQL_DB, user=settings.PGSQL_USER, 
#         password=settings.PGSQL_PASSWORD, host=settings.PGSQL_HOST, port=settings.PGSQL_PORT):
#         self.conn = None
#         self.cur = None
#         self.pool = None

#         self.dbname = dbname
#         self.user = user
#         self.password = password
#         self.host = host
#         self.port = port

#         # connect to the PostgreSQL server
#         try:
#             # self.conn = psycopg2.connect(**params)
#             # Create a connect pool to database
#             self.pool = ThreadedConnectionPool(5, 100,
#                 f"dbname={self.dbname} user={self.user} password={self.password} \
#                     host={self.host} port={self.port}") 
#         except (Exception, psycopg2.DatabaseError) as error:
#             self.pool.closeall()
#             logger.debug("Failed to create connection pool.", error)

#     def exit(self):
#         self.pool.closeall() # Close all the connections in the pool
#         pass

#     def execute(self, sql_commands, data=None):
#         try:
#             self.conn = self.pool.getconn()
#             self.cur = self.conn.cursor()
#             for sql_command in sql_commands:
#                 self.cur.execute(sql_command, data)
#             self.conn.commit()
#             return self.cur.fetchone()[0]
            
#         except (Exception, psycopg2.DatabaseError) as error:
#             # logger.debug(error)
#             raise error
#         finally:
#             # Close cur and discard current connect 
#             if self.cur is not None:
#                 self.cur.close()
#             if self.conn is not None:
#                 self.pool.putconn(self.conn, close=False) # Put away a connection
#                 # logger.info("Database connection closed.")

#     def create_tables(self, sql_commands=None):
#         """create tables in the PostgreSQL database"""

#         if sql_commands is None:
#             logger.warning("No sql commands to execute.")
#             sql_commands = create_sql_commands
#         try:
#             self.execute(sql_commands)
#         except Exception as err:
#             logger.debug(err)

#     def __insert(self, table_name=None, fields=None, data=None):
#         """ insert data into table """

#         if table_name is None:
#             logger.debug("Table name could not be empty")
#             return
#         if fields is None:
#             logger.debug("Table fields could not be empty")
#             return 
#         if data is None:
#             logger.warning("Nothing to insert.")
#             return
        
#         cols = ", ".join(fields) 
#         fstr = ", ".join(["%s",] * len(fields))
#         sql_command = (f"""
#             INSERT INTO {table_name} ({cols})
#             VALUES ({fstr});
#             """,)
#         logger.info(f"[INSERT] INTO {table_name}", data)
#         try:
#             self.execute(sql_command, data)
#         except Exception as err:
#             logger.debug(err)

#     def insert_price(self, table_name=None, fields=None, data=None):
#         """ insert a new price record into the toke_price table """
#         return self.__insert(table_name=table_name, fields=fields, data=data)

#     def insert_info(self, table_name=None, fields=None, data=None):
#         """ insert a new info record into the toke_info table """
#         logger.info("Successfuly insert a data.")
#         return self.__insert(table_name=table_name, fields=fields, data=data)

#     def query(self, fields=None, tables=None, cons=None):
#         sql_command = (f"""
#             SELECT {fields}
#             FROM {tables}
#             WHERE {cons}
#         """,)
#         try:
#             return self.execute(sql_command)
#         except Exception as err:
#             logger.debug(err)

class TokenDB(object):

    def __init__(self, dbname=settings.PGSQL_DB, user=settings.PGSQL_USER, 
                password=settings.PGSQL_PASSWORD, host=settings.PGSQL_HOST,
                port=settings.PGSQL_PORT, table_name=None, fields=None):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.table_name = table_name
        self.fields = fields

        self.conn = psycopg2.connect(dbname=self.dbname, 
                                    user=self.user,
                                    password=self.password,
                                    host=self.host, 
                                    port=self.port,
                                    options="-c search_path=public")

    # def execute(self, sql_command, datas=None):
    #     '''执行单条SQL语句，如需执行多条SQL语句，需要在外部迭代调用execute'''
    #     with self.conn:
    #         with self.conn.cursor() as cur:
    #             if datas is not None and isinstance(datas[0], list):
    #                 cur.executemany(sql_command, datas)
    #             else:
    #                 cur.execute(sql_command, datas)
    #             self.conn.commit()
    #             try:
    #                 return cur.fetchall()
    #             except Exception as e:
    #                 logger.info('No result to fetch.')

    def table_exists(self):
        """ Check if a table is exists. """
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)", (self.table_name,))
                return cur.fetchone()[0]

    def create_table(self, sql_commands=None):
        """ Create tables in the PostgreSQL database"""

        if self.table_exists():
            logger.info(f'[TABLE] {self.table_name} is existed. Skip creating table. ')
            return
        if sql_commands is None:
            logger.warning("No sql commands to execute.")
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    for sql_command in sql_commands:
                        cur.execute(sql_command)
                self.conn.commit()
        except psycopg2.errors.DependentObjectsStillExist as e:
            raise e

    def insert(self, datas=None):
        """ insert data into table """

        if self.table_name is None:
            logger.debug("Table name could not be empty")
            return None
        if self.fields is None:
            logger.debug("Table fields could not be empty")
            return None
        if datas is None:
            logger.warning("Nothing to insert.")
            return None
        
        cols = ", ".join(self.fields) 
        fstr = ", ".join(["%s",] * len(self.fields))
        sql_command = (f"""
            INSERT INTO {self.table_name} ({cols})
            VALUES ({fstr});
            """)
        
        if isinstance(datas, tuple):
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(sql_command, datas)
                self.conn.commit()
        else:
           with self.conn:
                with self.conn.cursor() as cur:
                    print("---------->>", datas)
                    cur.executemany(sql_command, datas)
                self.conn.commit()
        
    def __del__(self):
        self.conn.close()

class TokenInfoDB(TokenDB):

    table_name = 'token_info'
    fields = ['address', 'created_time', 'name', 'symbol', 'decimal', 'type', 'uri']
    def __init__(self, table_name=None, fields=None):
        super().__init__(table_name=TokenInfoDB.table_name, fields=TokenInfoDB.fields)

    create_info_table = (
                    """
                    DROP TYPE IF EXISTS token_type;
                    """,
                    """
                    CREATE TYPE token_type AS ENUM ('ERC-20', 'ERC-721');
                    """,  
                    """
                    CREATE TABLE token_info(
                        address VARCHAR(42) PRIMARY KEY,
                        created_time TIMESTAMP NOT NULL DEFAULT current_timestamp, 
                        name VARCHAR(255) NOT NULL,
                        symbol VARCHAR(255) NOT NULL,
                        decimal INTEGER,
                        type token_type,
                        uri VARCHAR(255)
                    );
                """)

    def create_table(self, sql_commands=None):
        if sql_commands is None:
            sql_commands = TokenInfoDB.create_info_table
        return super().create_table(sql_commands=sql_commands)

    def get_by_address(self, field, address):

        sql_command = (f"""
        SELECT {field}
        FROM token_info
        WHERE address = %s;
        """)
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(sql_command, (address,))
                    return cur.fetchone()
        except psycopg2.ProgrammingError  as e:
            logger.info(f"There is no token in address:{address} in token_info database.")
            return None

    def get_decimal_by_address(self, address):
        return self.get_by_address(field='decimal', address=address)

    def get_name_by_address(self, address):

        return self.get_by_address(field='name', address=address)

    def get_symbol_by_address(self, address):

        return self.get_by_address(field='symbol', address=address)

    def get_address_list(self):

        sql_command = ("""
        SELECT address FROM token_info
        """)
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(sql_command)
                    return [res[0] for res in cur.fetchall()]
        except psycopg2.ProgrammingError as e:
            logger.info('Failed to get all token address list.')
            return []

class TokenPriceDB(TokenDB):

    def __init__(self, table_name='token_price', fields=['address', 'price', 'time', 'status', 'tvl', 'total_supply', 'api_tag', 'ex_tag']):
        super().__init__(table_name=table_name, fields=fields)

    create_price_table = ("""
                DROP TYPE IF EXISTS price_status;
                """,
                """  
                CREATE TYPE price_status AS ENUM ('Active', 'Failed', 'Unknown');
                """,
                """
                CREATE TABLE token_price(
                    address VARCHAR(42) NOT NULL,
                    price NUMERIC,
                    time TIMESTAMP NOT NULL DEFAULT current_timestamp,
                    status price_status NOT NULL DEFAULT 'Active',
                    tvl NUMERIC,
                    total_supply NUMERIC,
                    api_tag VARCHAR(255),
                    ex_tag VARCHAR(255)
                );
            """)

    def create_table(self, sql_commands=None):
        if sql_commands is None:
            sql_commands = TokenPriceDB.create_price_table
        return super().create_table(sql_commands=sql_commands)

    def get_price(self, address, time, limit=1):
        """ Get one token's latest price by address. """
        
        sql_command = ("""
        SELECT status, price, time
        FROM token_price
        WHERE address = %s AND time < %s
        ORDER BY time DESC
        LIMIT %s
        """)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql_command, (address, time, limit))
                return cur.fetchall()
            
if __name__ == '__main__':
    token_price_db = TokenPriceDB()
    res = token_price_db.get_price('0x208bbb6bcea22ef2011789331405347394ebaa51')
    
    # res = token_price_db.get_latest_price('0x053e5ba7cb9669dcc2feb2d0e1d3d4a0ad6aae39')
    print(type(res))
    print(res[0], res[1], res[2])
    # print(res[0])
    # token_info_db = TokenInfoDB()
    # print(token_info_db.get_address_list())
    # token_price_db = TokenPriceDB()
    # try:
    #     token_info_db.create_table()
    #     token_price_db.create_table()
    # except Exception as e:
    #     tmp = token_info_db.get_symbol_by_address('0x208bbb6bcea22ef2011789331405347394ebaa51')
    #     if not tmp:
    #         print(tmp, 'is empty')
    #     print(tmp[0][0])
        # import datetime
        # data = ['0x10100101010', 1202, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'), 'Active', 'huobi']
        # token_price_db.insert(data)
        # datas = []
        # for i in range(10):
        #     tmp = ['0x001940294014', i+100, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'), 'Active', 'huobi']
        #     datas.append(tmp)
        # token_price_db.insert(datas)
        # data = ['0x2039103', datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'), 'sat', 'eqt', 100, 120, 18, 'ERC-20', 'www.fuck.com']
        # # token_info_db.insert(data)
        # datas = []
        # for i in range(9):
        #     data[0] = '0x1932014' + str(i)
        #     datas.append(data.copy())
        # # print(datas)
        # token_info_db.insert(datas)
        # addrs = token_info_db.get_address_list()
        # print(addrs)
        # print(type(addrs))
        # print(len(addrs))
        # for addr in addrs:
        #     print(type(addr))
        #     print(addr[0])
        # # print("ttttt")
        # print([t[0] for t in addrs])
        

    # print(TOKEN_DB.get_address_by_name('BTC'))
    # token_info_db = TokenInfoDB()
    # print(token_info_db.get_address_by_name('BTC'))
    



    # db.create_tables()
    #     # address = '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2'
    # # price = 2210126942396954
    # # time = '2021-05-10'
    # # origin = 'coin_gecko' 
    # for i in range(10):
    #     price_data = {
    #         'address':f'0x{i}f8f72aa9304c8b593d555f12ef6589cc3a579a2',
    #         'price': 2210126942396954,
    #         'time': datetime.date(2021, 5, 10),
    #         "status": 'Active',
    #         'origin': 'coin_gecko'
    #     }
    #     db.insert_price("token_price", list(price_data.keys()), list(price_data.values()))
    # info_data = {
    #     'address': f'0x140ef83ec8560892168d4062720f0s0460468656',
    #     'name': 'Ethereum Meta',
    #     'symbol': 'ETHM',
    #     'decimal': 18,
    #     'type': 'ERC-20',
    #     'uri': None
    # }
    # token_info_db.insert_info("token_info", list(info_data.keys()), list(info_data.values()))
    # addr = '0x3f8f72aa9304c8b593d555f12ef6589cc3a579a2'
    # res = TOKEN_DB.query(fields="price", tables="token_price", cons=f"address = '{addr}'")
    # print(res)