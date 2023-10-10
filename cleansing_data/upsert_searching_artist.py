import pandas as pd
import pymysql
import os
import sys
from sshtunnel import SSHTunnelForwarder
# DB 연결
from dotenv import load_dotenv
from sqlalchemy import create_engine
import re

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
        
        base_url = "/Users/hanseungjae/auction_solution/data_cleansing/0626/"
        df = pd.read_excel(base_url+"bio_clean.xlsx")

        # define column in database
        db_columns = ["id","artist_id","name_kr","name_en","born", "dead"]
        matching_columns = [col for col in df.columns if col in db_columns]
        data = df[matching_columns]

        ids_from_excel = data["artist_id"].tolist() # get id from excel file
        #ids_from_excel = data["id"].apply(lambda x: re.sub(r"[',\"]", "", str(x))).tolist()

        id_place_holders = ",".join([f"'{i}'" for i in ids_from_excel])

        query = f"SELECT id FROM artist_searching_data WHERE id IN ({id_place_holders})"
        ids_from_db = pd.read_sql(query, conn)
        ids_from_db = ids_from_db["id"].tolist()

        ids_be_update = []
        ids_be_insert = []
        
        # compare
        for id_excel in ids_from_excel:
            if id_excel in ids_from_db:
                ids_be_update.append(id_excel)
            else:
                ids_be_insert.append(id_excel)

        print("id will update:", ids_be_update, "\n", "id will insert", ids_be_insert)

        if len(ids_be_update) > 0:
            # To do: update
            pd_be_update = data.loc[df['id'].isin(ids_be_update)]
            
            for i, row in pd_be_update.iterrows():
                insert_columns = [col for col in matching_columns]
                insert_values = [f"{row[col]}" for col in matching_columns]
                insert_values = [None if x == 'nan' else x for x in insert_values]
                auction_id = row['id']
                set_values = []
                for column, value in zip(insert_columns, insert_values):
                    if value:
                        # Escape single quotes in the value
                        value = re.sub("'", "''", value)
                        set_values.append(f"{column} = '{value}'")
                    else:
                        set_values.append(f"{column} = NULL")
                set_values_str = ", ".join(set_values)
                query = f"UPDATE artist_searching_data SET {set_values_str} WHERE id = {auction_id}"
                cursor.execute(query)
            cursor.execute("COMMIT;")

        if len(ids_be_insert) > 0:
            # todo: insert
            pd_be_insert = data.loc[df['id'].isin(ids_be_insert)]

            for i, row in pd_be_insert.iterrows():
                insert_columns = ", ".join([f"{col}" for col in matching_columns])
                insert_values = [f"{row[col]}" for col in matching_columns]
                insert_values = [None if x == 'nan' else x for x in insert_values]

                values = []
                for value in insert_values:
                    if value:
                        # Escape single quotes in the value
                        value = re.sub("'", "''", value)
                        values.append(f"'{value}'")
                    else:
                        values.append("NULL")
                values_str = ", ".join(values)
                
                query = f"INSERT INTO artist_searching_data ({insert_columns}) VALUES ({values_str})"
                cursor.execute(query)
            
            cursor.execute("COMMIT;")
