from flask import Flask, request, make_response, send_from_directory

from flask_restful import Resource, Api
import pymysql
import setting
import crypt
import json
import time
import datetime
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import base64

app = Flask(__name__)
connect_db_list = dict()

"""
api/search_data post
in
keywords    string  

out
msg    string
datalist    list
"""
@app.route('/api/search_data', methods=['POST'])
def search_data():
    _result_msg = "done"
    _datalist = []

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _keywords = _jsonData['keywords']

    _limit = 0

    if "limit" in _jsonData:
        _limit = _jsonData['limit']

    try:
        bdb = BigchainDB(setting.blockchain_db_url)
        _datalist = bdb.assets.get(search=_keywords,limit=_limit)
        _result_msg = "search data is done."

    except Exception as e:
        _result_msg = e

    _resultDict = dict(msg=("%s") % (_result_msg), datalist=_datalist)
    return _resultDict

"""
api/get_data post
in
blockid    string  

out
msg    string
data    string
"""
@app.route('/get_data', methods=['POST'])
def get_data():
    _result_msg = "done"

    _blockdata = ""

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _blockid = _jsonData['blockid']

    try:
        bdb = BigchainDB(setting.blockchain_db_url)
        _assertdata = bdb.assets.get(search=_blockid)

        if len(_assertdata) > 0:
            if "data" in _assertdata[0]:
                _blockdata = _assertdata[0]["data"]["blockdata"]
                _result_msg = "find data done!"
            else:
                _result_msg = "don't have data !"
        else:
            _result_msg = "don't find blockid data !"

    except Exception as e:
        _result_msg = e

    _resultDict = dict(msg=("%s") % (_result_msg), data=_blockdata)
    return _resultDict

"""
api/block_height post
in
blockid    string  [if it's empty , return the chain height]

out
msg    string
blockheight    string
"""
@app.route('/api/block_height', methods=['POST'])
def block_height():
    _result_msg = "done"

    _block_height = ""

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _blockid = _jsonData['blockid']

    try:

        if len(_blockid) > 0:

            bdb = BigchainDB(setting.blockchain_db_url)
            _block_height = bdb.blocks.get(txid=_blockid)

        else:

            mydb = pymysql.connect(**setting.mysql_config)
            dbcursor = mydb.cursor()

            sql_str = """select * from %s.record where record.operate='CREATE' order by record.uid DESC limit 1;""" % (setting.mysql_db_name)
            _mysql_rst = dbcursor.execute(sql_str)
            _mysql_result = dbcursor.fetchall()

            if _mysql_rst == 1:
                _mysql_result = _mysql_result[0]
                _block_height = _mysql_result["block"]

            mydb.commit()
            mydb.close()

        _result_msg = "block_height get done.";
    except Exception as e:
        _result_msg = e

    _resultDict = dict(msg=("%s") % (_result_msg), blockheight=_block_height)
    return _resultDict

"""
api/push_data post
in
key    string  
data    string
 * index_key    string

out
msg    string
blockid    string
blockheight    string
"""
@app.route('/api/push_data', methods=['POST'])
def push_data():
    _result_msg = "done"
    _block_id = ""
    _block_height = ""

    data_asset = {
        'data': {
            'index_key':'',
            'blockdata':{

            },
        },
    }

    data_asset_metadata = {
        'time': '',
        'user': '',
    }

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _userkey = _jsonData['key']

    if _userkey in connect_db_list:

        _username = connect_db_list[_userkey]["username"]
        _public_key = connect_db_list[_userkey]["public_key"]
        _private_key = connect_db_list[_userkey]["private_key"]

        data_asset["data"]["blockdata"] = _jsonData['data']

        if "index_key" in _jsonData:
            data_asset["data"]["index_key"] = _jsonData['index_key']
        else:
            data_asset["data"]["index_key"] = _username

        _date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        data_asset_metadata["time"] = _date
        data_asset_metadata["user"] = _username

        try:
            bdb = BigchainDB(setting.blockchain_db_url)

            prepared_creation_tx = bdb.transactions.prepare(
                operation='CREATE',
                signers=_public_key,
                asset=data_asset,
                metadata=data_asset_metadata
            )

            fulfilled_creation_tx = bdb.transactions.fulfill(
                prepared_creation_tx,
                private_keys=_private_key
            )

            _sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

            _txid = fulfilled_creation_tx['id']

            _block_height = bdb.blocks.get(txid=_txid)

            _block_id = _txid;

            mydb = pymysql.connect(**setting.mysql_config)
            dbcursor = mydb.cursor()

            sql_str = """insert into %s.record(record.user,record.date,record.assert,record.block,record.operate) values ('%s','%s','%s','%s','CREATE');""" % (setting.mysql_db_name,_username,_date,_block_id,_block_height)
            _mysql_rst = dbcursor.execute(sql_str)
            mydb.commit()
            mydb.close()

            _result_msg = "push data to db done.";
        except Exception as e:
            _result_msg = e

    else:
        _result_msg = "user don't connected the db.";

    _resultDict = dict(msg=("%s") % (_result_msg), blockid=_block_id,blockheight=_block_height)
    return _resultDict

"""
api/search_userkey post
in
username    string
userpassword    string

out
msg    string
key    string
"""
@app.route('/api/search_userkey', methods=['POST'])
def close_db():
    _result_msg = "done"
    _userkey = ""

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _username = _jsonData['username']
    _userpassword = _jsonData['userpassword']

    try:
        mydb = pymysql.connect(**setting.mysql_config)
        dbcursor = mydb.cursor()
        sql_str = """select * from %s.user where user.name='%s' and user.password='%s';""" % (setting.mysql_db_name, _username,_userpassword)
        _mysql_rst = dbcursor.execute(sql_str)
        _mysql_result = dbcursor.fetchall()

        if _mysql_rst == 1:
            _result_msg = "search done !"
            _mysql_result = _mysql_result[0]
            _userkey = _mysql_result["key"]
        else:
            _result_msg = "Don't find the user!"

    except Exception as e:
        _result_msg = e
    finally:
        mydb.close()

    _resultDict = dict(msg=("%s") % (_result_msg),key=_userkey)
    return _resultDict

"""
api/connect_db post
in
key    string

out
msg    string
"""
@app.route('/api/connect_db', methods=['POST'])
def connect_db():
    _result_msg = "done"
    _userkey = ""

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _userkey = _jsonData['key']

    try:
        mydb = pymysql.connect(**setting.mysql_config)
        dbcursor = mydb.cursor()

        _datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        sql_str = """select * from %s.user where user.key='%s';""" % (setting.mysql_db_name, _userkey)
        _mysql_rst = dbcursor.execute(sql_str)
        _mysql_result = dbcursor.fetchall()

        if _mysql_rst == 1:
            _result_msg = "Connect chain_db is done !"
            _mysql_result = _mysql_result[0]

            connect_db_list[_userkey] = dict(username=_mysql_result["name"],public_key=_mysql_result["public_key"],private_key=_mysql_result["private_key"],connecttime=_datetime)

            sql_str = """update %s.user set user.lastlogin_date = '%s' where user.key='%s';""" % (setting.mysql_db_name, _datetime, _userkey)
            _mysql_rst = dbcursor.execute(sql_str)
            mydb.commit()

        else:
            _result_msg = "Connect chain_db is error , don't find the key!"

    except Exception as e:
        _result_msg = e
    finally:
        mydb.close()

    _resultDict = dict(msg=("%s") % (_result_msg))
    return _resultDict

"""
api/generate_key post
in
username    string
userpassword    string

out
msg    string
user_key    string
"""
@app.route('/api/generate_key', methods=['POST'])
def generate_key():
    _result_msg = "done"
    _userkey = ""
    _public_key = ""
    _private_key = ""

    _jsonData = request.get_json()
    user_agent = request.headers.get('User-Agent', "")

    if type(_jsonData) is str:
        _jsonData = json.loads(request.get_json())

    _username = _jsonData['username']
    _userpassword = _jsonData['userpassword']

    try:
        mydb = pymysql.connect(**setting.mysql_config)
        dbcursor = mydb.cursor()

        sql_str = """SELECT * FROM %s.user WHERE name = '%s'; """ % ( setting.mysql_db_name,_username)

        _mysql_rst = dbcursor.execute(sql_str)
        _mysql_result = dbcursor.fetchall()

        if _mysql_rst > 0:
            _result_msg = "That username is already in use!"
        else:
            _datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            _salt = crypt.mksalt(crypt.METHOD_SHA512)

            _hash = crypt.crypt("%s_%s_%s" % (_username, _userpassword, _datetime), _salt)

            _userkey_bytes = base64.b64encode(('%s'%(_hash)).encode(encoding="utf-8"))
            _userkey = str(_userkey_bytes, encoding="utf-8")
            _keypair_chaindb = generate_keypair()

            _public_key = _keypair_chaindb.public_key
            _private_key = _keypair_chaindb.private_key

            _lastlogin = _datetime

            sql_str = """insert into %s.user(user.name,user.password,user.key,user.public_key,user.private_key,user.salt,user.generate_date,user.lastlogin_date) values ('%s','%s','%s','%s','%s','%s','%s','%s');""" % (setting.mysql_db_name,_username, _userpassword, _userkey, _public_key, _private_key,_salt, _datetime, _lastlogin)
            _mysql_rst = dbcursor.execute(sql_str)
            mydb.commit()
            _result_msg = "generate_key done"

    except Exception as e:
        _result_msg = e
        _userkey = ""
    finally:
        mydb.close()

    _resultDict = dict(msg=("%s") % (_result_msg), user_key=_userkey)
    return _resultDict

if __name__ == '__main__':
    _host = '0.0.0.0'
    _port = 8888

    app.run(
        host=_host,
        port=_port,
        threaded=True,
        debug=False
    )