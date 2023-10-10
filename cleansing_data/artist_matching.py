import pandas as pd
import pymysql
import os
import sys
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from sqlalchemy import create_engine
import re

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.appendDB import connect_RDS

# DB 연결
def connect_RDS(host, username, password, database, port):
    try:
        conn = pymysql.connect(
            host=host,
            user=username,
            passwd=password,
            db=database,
            port=port,
            use_unicode=True,
            charset="utf8",
        )
        cursor = conn.cursor()
        print("RDS에 연결되었습니다.")
    except:
        print("RDS에 연결되지 않았습니다")
        sys.exit(1)
    return conn, cursor
load_dotenv()
# DB server연결
with SSHTunnelForwarder(
        (os.environ.get("prod_SSH_host")),
        ssh_username=os.environ.get("SSH_user"),
        ssh_pkey=os.environ.get("new_SSH_key"),
        remote_bind_address=(os.environ.get("prod_DB_host"), int(os.environ.get("DB_port"))),
    ) as tunnel:
        host = "127.0.0.1"
        username = os.environ.get("DB_username")
        password = os.environ.get("DB_password")
        database = os.environ.get("new_DB_database")
        port = tunnel.local_bind_port
        conn, cursor = connect_RDS(host, username, password, database, port)
        


try:
    # 커서 생성
    cursor = connect_RDS.cursor()

    # solution_yeolmae.need_cleansing_data 테이블과 solution_yeolmae_artist 테이블을 조인하여 artist_id 값을 업데이트
    query = """
    UPDATE solution_yeolmae_crawling AS c
    INNER JOIN solution_yeolmae_artist AS a ON c.artist_kor = a.name_kr
                                        AND c.artist_birth = a.born
                                        AND c.artist_death = a.dead
    SET c.artist_id = a.id,
        c.artist_birth = a.born,
        c.artist_death = a.dead
    """
    cursor.execute(query)

    # 변경사항을 커밋하여 DB에 반영
    connect_RDS.commit()

finally:
    # 연결 닫기
    connect_RDS.close()