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
    ("ec2-13-125-232-249.ap-northeast-2.compute.amazonaws.com"),
    # back server usesr name
    ssh_username="ubuntu",
    # key 파일 위치
    ssh_pkey="/Users/hanseungjae/pem/key-new-auction.pem",
    # DB(RDS) server 주소
    remote_bind_address=("db-auction.cq6auf3da3a6.ap-northeast-2.rds.amazonaws.com", 3306) 
)as tunnel:
    host= '127.0.0.1'
    # DB user name
    username ="admin"
    # DB pw
    password="fXf384j2d823j!fjwWDgsaD13"
    # DB database name
    database = "solution_yeolmae" 
    port = tunnel.local_bind_port
    conn, cursor = connect_RDS(host,username,password,database,port)

    query = "SELECT * FROM solution_yeolmae.need_cleansing_data where transact_date < '2023-10-01' and material_kind in ('Paintin','Works on paper','Edition') and height is not null and size_table is null; "
    #query = "SELECT * FROM solution_yeolmae.crawling where transact_date ='2023-10-04' "
    #query = "SELECT * FROM solution_yeolmae.crawling where bid_class = 'w/d' "
    #query = "SELECT * FROM solution_yeolmae.prod_auction_data"
    #query = "SELECT * FROM solution_yeolmae.artist where id = 1"
    #query = "SELECT * FROM (SELECT artist_kor,COUNT(*) AS count FROM solution_yeolmae.crawling WHERE artist_kor IS NOT NULL AND artist_id IS NULL GROUP BY artist_kor) AS subquery ORDER BY count DESC;;"
    
    db_data = pd.read_sql(query,conn)
    conn.close()
     #filename = table_name+".xlsx"
    filename = "size_table.xlsx"
    print(filename +"을 엑셀파일로 저장합니다.")
    db_data.to_excel(filename, index = False)
