from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from time import sleep
from sys import exit

bdb_root_url = 'http://192.168.96.129:9984'  # Use YOUR BigchainDB Root URL here

bdb = BigchainDB(bdb_root_url)

json_str = bdb.assets.get(search="abcd1234")

print(json_str)

json_str = bdb.transactions.get(asset_id="220429eec0814dccdfb021370c03f568182233fe6554c900c0571e9b70801f99")

print(json_str)