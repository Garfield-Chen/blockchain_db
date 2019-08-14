import pymysql

mysql_self_config = {
          'host':'192.168.96.1',
          'port':3306,
          'user':'blockchain_demo',
          'password':'blockchain_demo',
          'db':'blockchain_demo',
          'charset':'utf8mb4',
          'cursorclass':pymysql.cursors.DictCursor,
          }

mysql_config = mysql_self_config
mysql_db_name = "blockchain_demo"

server_log = "./log/"


blockchain_db_url = 'http://192.168.96.129:9984'  # Use YOUR BigchainDB Root URL here

# ORM 数据库连接
"""
engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset={charset}".format(**mysql_config),
                        # encoding = "utf8mb4",
                        pool_size = 150,
                        pool_recycle = 7200,
                        echo=False)
session_factory = sessionmaker(bind=engine)
db_session = scoped_session(session_factory)
"""