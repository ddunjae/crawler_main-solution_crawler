import os
import sys
import boto3
from dotenv import load_dotenv
import pandas as pd
from sshtunnel import SSHTunnelForwarder
from datetime import datetime
import pymysql
import pandas as pd
import urllib.parse
import furl

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import utility.appendS3 as appendS3

load_dotenv()

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("폴더생성에 실패했습니다.")

def connect_RDS(host, username, password, database, port):
    try:
        conn= pymysql.connect(host=host, user= username, passwd = password, db= database,port = port, use_unicode = True, charset = 'utf8')
        cursor = conn.cursor()
        print("RDS에 연결되었습니다.")
    except:
        print("RDS에 연결되지 않았습니다")
        sys.exit(1)
    return conn,cursor

with SSHTunnelForwarder(
    (os.environ.get("prod_SSH_host")),
    ssh_username=os.environ.get("SSH_user"),
    ssh_pkey=os.environ.get("new_SSH_key"),
    remote_bind_address=(os.environ.get("prod_DB_host"), int(os.environ.get("DB_port"))) 
)as tunnel:
    host= '127.0.0.1'
    username =os.environ.get("DB_username")
    password=os.environ.get("DB_password") 
    database =os.environ.get("new_DB_database")
    port = tunnel.local_bind_port
    conn, cursor = connect_RDS(host,username,password,database,port)

    AWS_REGION = os.environ.get("AWS_REGION")
    ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
    ACCESS_SECRET_KEY = os.environ.get("ACCESS_SECRET_KEY")
    BUCKET_NAME = os.environ.get("BUCKET_NAME")

    s3 = boto3.client(
        service_name="s3",
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
    )

    wrong_img_query = "SELECT id, company, transact_date, lot, img, auction_name FROM solution_yeolmae.need_cleansing_data WHERE img NOT LIKE '%https://new-auction-solution.s3.ap-northeast-2.amazonaws.com%' AND img LIKE 'http%' AND transact_date = '2023-09-19' "
  
    df = pd.read_sql(wrong_img_query, conn)
    if df.empty:
        print("don't have wrong img link")
        exit()
    for index, row in df.iterrows():
        df.at[index, "img"] =  furl.furl(row["img"]).url

    filename = "{0}_{1}.xlsx".format(
        'old_img_link', str(datetime.now().strftime("%y%m%d_%H%M"))
    )
    df.to_excel(filename, index=False)

    temp = {
        "id": [],
        "company": [],
        "transact_date": [],
        "lot": [],
        "img": [],
        "auction_name": []
    }

    df = appendS3.main(df, temp)

    filename = "{0}_{1}.xlsx".format(
        'new_img_link', str(datetime.now().strftime("%y%m%d_%H%M"))
    )
    df.to_excel(filename, index=False)

    for index, row in df.iterrows():
        query = f"UPDATE solution_yeolmae.need_cleansing_data SET img = '{row['img']}' WHERE id = {row['id']}"
        cursor.execute(query)
    cursor.execute("commit;")