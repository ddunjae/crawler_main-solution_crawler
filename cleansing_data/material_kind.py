"""
    This is handle multiple row which it has no null value material_kind
"""

import pandas as pd
import sys
import pymysql
import pandas as pd
import numpy as np
import os
from cmath import nan
from sshtunnel import SSHTunnelForwarder
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Material import Material

load_dotenv()

def connect_RDS(host, username, password, database, port):
    try:
        conn= pymysql.connect(host=host, user= username, passwd = password, db= database,port = port, use_unicode = True, charset = 'utf8')
        cursor = conn.cursor()
        print("RDS에 연결되었습니다.")
    except:
        print("RDS에 연결되지 않았습니다")
        sys.exit(1)
    return conn,cursor



#RDS info
with SSHTunnelForwarder(
    # backend server 주소
    (os.environ.get("prod_SSH_host")),
    # back server usesr name
    ssh_username=os.environ.get("SSH_user"),
    # key 파일 위
    ssh_pkey=os.environ.get("new_SSH_key"),
    # DB(RDS) server 주소
    remote_bind_address=(os.environ.get("prod_DB_host"), int(os.environ.get("DB_port"))) 
)as tunnel:
    host= '127.0.0.1'
    # DB user name
    username =os.environ.get("DB_username")
    # DB pw
    password=os.environ.get("DB_password") 
    # DB database name
    database =os.environ.get("new_DB_database")
    port = tunnel.local_bind_port
    conn, cursor = connect_RDS(host,username,password,database,port)

    # handle material_kind from database
    # material_kind_null_query = "SELECT id, material_kind, material_eng, material_kor FROM solution_yeolmae.crawling WHERE material_kind IS NULL AND (material_eng IS NOT NULL OR material_kor IS NOT NULL);"
    # total_data_query = "SELECT count(*) AS total FROM solution_yeolmae.crawling WHERE material_kind IS NULL AND (material_eng IS NOT NULL OR material_kor IS NOT NULL);"
    # db_data = pd.read_sql(material_kind_null_query, conn)
    # total_data = pd.read_sql(total_data_query, conn)

    # handle size_table from excel
    base_url = "/Users/hanseungjae/auction_solution/data_cleansing/1005/"
    data = pd.read_excel(base_url+"1002k.xlsx")
    if data.empty:
        print('No data for handle')
    else:
        # handle material_kind
        for index, row in data.iterrows():
            material_kind = Material(row['material_eng'], row['material_kor'], "")
            query = f"UPDATE need_cleansing_data SET material_kind = '{material_kind}' WHERE id = {row['id']}"
            cursor.execute(query)
        cursor.execute("commit;")
