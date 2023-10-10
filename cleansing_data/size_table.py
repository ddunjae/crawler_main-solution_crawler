"""
    This is handle multiple row which it has no null value size_table
"""

import pandas as pd
import sys
import pymysql
import numpy as np
import os
from cmath import nan
from sshtunnel import SSHTunnelForwarder
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Material import Material
from cleansing.CanvasSize import Canvas_size_not_depend_on_material_kind


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

    # handle size_table from database
    # size_table_null_query = "SELECT id, size_table, height, width, material_kind FROM solution_yeolmae.crawling WHERE size_table IS NULL AND height IS NOT NULL AND width IS NOT NULL;"
  
    # db_data = pd.read_sql(size_table_null_query, conn)


    # handle size_table from excel

    base_url = "/Users/hanseungjae/auction_solution/data_cleansing/1010/"
    data = pd.read_excel(base_url+"size_table.xlsx")

    if data.empty:
        print('No data for handle')
    else:
        # handle size_table
        for index, row in data.iterrows():
            size_table = Canvas_size_not_depend_on_material_kind(row['height'], row['width'])
            data.loc[index, 'size_table'] = size_table
            size_table = f"{size_table}" if size_table or size_table == 0 else "NULL"
            query = f"UPDATE need_cleansing_data SET size_table = {size_table} WHERE id = {row['id']}"
            cursor.execute(query)
        cursor.execute("commit;")
        conn.close()