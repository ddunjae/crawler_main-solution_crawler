from cmath import nan
from doctest import DocFileTest
import sys
import os
from tkinter import Frame
import numpy
import requests
import base64
import pymysql
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import re


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


# 테이블이 있는지 확인하고 없으면 테이블 생성.
def check_table(cursor, conn):
    query = """select count(*)
    from information_schema.TABLES
    where table_name = 'need_cleansing_data'"""
    if pd.read_sql(query, conn).values[0][0]:
        print("테이블 확인완료.")
    else:
        print("테이블이 존재하지 않아 생성합니다.")
        create = """CREATE TABLE need_cleansing_data(
                lot INT(11) NOT NULL,
                img TEXT,
                artist_kor TEXT,
                artist_eng TEXT,
                artist_birth int(4),
                artist_death int(4),
                title_kor TEXT,
                title_eng TEXT,
                mfg_date TEXT,
                certification TEXT,
                height FLOAT,
                width FLOAT,
                depth FLOAT,
                material_kind TEXT,
                material_kor TEXT,
                material_eng TEXT,
                signed TEXT,
                exhibited TEXT,
                provenance TEXT,
                frame TEXT,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                auction_name VARCHAR(255) NOT NULL,
                on_off TEXT NOT NULL,
                transact_date date NOT NULL,
                currency VARCHAR(8),
                start_price double,
                usd_start_price price FLOAT,
                hammer_price double,
                usd_hammer_price FLOAT,
                selling_price double,
                usd_selling_price FLOAT,
                estimate_min double,
                usd_estimate_min FLOAT,
                estimate_max double,
                usd_estimate_max FLOAT,
                competition FLOAT,
                etc TEXT,
                PRIMARY KEY(lot, auction_name)
                );"""
        cursor.execute(create)
        cursor.execute("alter table crawling_v1 convert to charset utf8;")


def main(df):
    load_dotenv()

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

        engine = create_engine(
            "mysql+pymysql://"
            + username
            + ":"
            + password
            + "@"
            + host
            + ":"
            + str(port)
            + "/"
            + database,
            connect_args={'charset':'utf8'},
        )

        check_table(cursor, conn)
        for auction_name in df.auction_name.unique():
            print(auction_name)
            company = df["company"].unique()[0]
            query = (
                "SELECT * FROM need_cleansing_data WHERE (auction_name = '"
                + auction_name
                + "' and company = '"
                + company
                + "');"
            )
            db_data = pd.read_sql(query, conn)
            
            if len(db_data) > 0:
                for lot, id_ in zip(db_data["lot"], db_data["id"]):
                    query = ""
                    if type(df.lot[0]) != numpy.int64:
                        lot = str(lot)

                    if (len(df.loc[(df.auction_name == auction_name) & (df.lot == lot)]) == 1):
                        hammer_price = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "hammer_price"].values[0]
                        usd_hammer_price = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "usd_hammer_price"].values[0]
                        selling_price = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "selling_price"].values[0]
                        usd_selling_price = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "usd_selling_price"].values[0]
                        usd_estimate_min = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "usd_estimate_min"].values[0]
                        usd_estimate_max = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "usd_estimate_max"].values[0]
                        usd_start_price = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "usd_start_price"].values[0]
                        bid_class = "'" + str(df.loc[(df.auction_name == auction_name) & (df.lot == lot), "bid_class"].values[0]) + "'"

                        artist_eng = "'" + str(df.loc[(df.auction_name == auction_name) & (df.lot == lot), "artist_eng"].values[0]) + "'"
                        artist_kor = "'" + str(df.loc[(df.auction_name == auction_name) & (df.lot == lot), "artist_kor"].values[0]) + "'"
                        artist_birth = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "artist_birth"].values[0]
                        artist_death = df.loc[(df.auction_name == auction_name) & (df.lot == lot), "artist_death"].values[0]

                        if not re.findall("[0-9]",str(hammer_price)): hammer_price ='NULL'
                        if not re.findall("[0-9]",str(usd_hammer_price)): usd_hammer_price ='NULL'
                        if not re.findall("[0-9]",str(selling_price)): selling_price ='NULL'
                        if not re.findall("[0-9]",str(usd_selling_price)): usd_selling_price ='NULL'
                        if not re.findall("[0-9]",str(usd_estimate_min)): usd_estimate_min ='NULL'
                        if not re.findall("[0-9]",str(usd_estimate_max)): usd_estimate_max ='NULL'
                        if not re.findall("[0-9]",str(usd_start_price)): usd_start_price ='NULL'
                        if not re.findall("above|within|below|w/d",str(bid_class).lower()): bid_class ='NULL'

                        if not re.findall("[0-9]",str(artist_birth)): artist_birth ='NULL'
                        if not re.findall("[0-9]",str(artist_death)): artist_death ='NULL'


                        query += "update need_cleansing_data set "
                        query += "hammer_price = {0}, ".format(hammer_price)
                        query += "usd_hammer_price = {0}, ".format(usd_hammer_price)
                        query += "selling_price = {0}, ".format(selling_price)
                        query += "usd_selling_price = {0}, ".format(usd_selling_price)
                        query += "usd_estimate_min = {0}, ".format(usd_estimate_min)
                        query += "usd_estimate_max = {0}, ".format(usd_estimate_max)
                        query += "usd_start_price = {0}, ".format(usd_start_price)
                        query += "bid_class = {0} , ".format(bid_class)

                        query += "artist_eng = {0}, ".format(artist_eng)
                        query += "artist_kor = {0}, ".format(artist_kor)
                        query += "artist_birth = {0}, ".format(artist_birth)
                        query += "artist_death = {0} ".format(artist_death)

                        query += "where id = {0}; ".format(id_)
                    else:
                        print("출품취소 : lot.{0}, (id={1})".format(lot, id_))
                        query += "update need_cleansing_data set "
                        query += "bid_class = 'w/d', "
                        query += "usd_hammer_price = null, "
                        query += "selling_price = null, "
                        query += "usd_selling_price = null "
                        query += "where id = {0}; ".format(id_)
                    cursor.execute(query)
                cursor.execute("commit;")
                print("테이블 업데이트")
                conn.close()
            else:
                try:
                    print("테이블 업데이트")
                    df.to_sql(
                        name="need_cleansing_data", con=engine, if_exists="append", index=False
                    )
                except Exception as e:
                    print(e)


#crawling
#need_cleansing_data
#need_cleansing_data_sy 