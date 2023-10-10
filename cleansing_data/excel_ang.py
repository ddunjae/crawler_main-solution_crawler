import pandas as pd
import platform
from selenium import webdriver
import os
from datetime import datetime
import sys
import os
import requests
import base64
import pymysql
import pandas as pd
import numpy as np
from cmath import nan
from sshtunnel import SSHTunnelForwarder
import sys



def connect_RDS(host, username, password, database,port):
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
    ("ec2-3-39-233-62.ap-northeast-2.compute.amazonaws.com"),
    # back server usesr name
    ssh_username="ubuntu",
    # key 파일 위치
    ssh_pkey="/Users/hanseungjae/pem/key-art.pem",
    # DB(RDS) server 주소
    remote_bind_address=("db-prod-art.cineckgesfth.ap-northeast-2.rds.amazonaws.com", 3306) 
)as tunnel:
    host= '127.0.0.1'
    # DB user name
    username ="admin"
    # DB pw
    password="f32h79HGr35^G&HG*#Fg3"
    # DB database name
    database = "artnguide_scheme" 
    port = tunnel.local_bind_port
    conn, cursor = connect_RDS(host,username,password,database,port)

    query = "SELECT * FROM artnguide_scheme.group_purchase where id = 182;"

    
    db_data = pd.read_sql(query,conn)
    conn.close()
     #filename = table_name+".xlsx"
    filename = "이우환untitled.xlsx"
    print(filename +"을 엑셀파일로 저장합니다.")
    db_data.to_excel(filename, index = False)
