import pandas as pd
import pymysql
import os
import sys
from sshtunnel import SSHTunnelForwarder
# DB 연결
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
        
        
        base_url = "/Users/hanseungjae/auction_solution/data_cleansing/0526/"
        df = pd.read_excel(base_url+"raiz_del.xlsx")

        # define column in database
        db_columns = ["id", "company", "auction_name", "on_off", "location", "transact_date", "lot", "img", "artist_id", "artist_kor", "artist_eng", "artist_birth", "artist_death", "title_kor", "title_eng", "mfg_date", "height", "width", "depth", "size_table", "material_kind", "material_kor", "material_eng", "signed", "exhibited", "provenance", "literature", "catalogue", "frame", "certification", "condition_report", "description", "currency", "start_price", "hammer_price", "selling_price", "estimate_min", "estimate_max", "usd_start_price", "usd_hammer_price", "usd_selling_price", "usd_estimate_min", "usd_estimate_max", "competition", "bid_class", "method", "series", "main_color", "preference", "historical_category", "identical_records",]
        matching_columns = [col for col in df.columns if col in db_columns]
        data = df[matching_columns]

        ids_from_excel = data["id"].tolist() # get id from excel file

        id_place_holders = ",".join([f"{i}" for i in ids_from_excel])

        query = f"SELECT id FROM crawling WHERE id IN ({id_place_holders})"
        ids_from_db = pd.read_sql(query, conn)
        ids_from_db = ids_from_db["id"].tolist()

        ids_be_delete = []
        
        # compare
        for id_excel in ids_from_excel:
            if id_excel in ids_from_db:
                ids_be_delete.append(id_excel)
            else:
                x=id_excel
                print('id =' +str(id_excel)+'은 존재하지않는 데이터입니다.')
                
        print("id will delete:", ids_be_delete)

        if len(ids_be_delete) > 0:
            # To do: delete
            pd_be_delete = data.loc[df['id'].isin(ids_be_delete)]
            
            for i, row in pd_be_delete.iterrows():
                insert_columns = [col for col in matching_columns]
                insert_values = [f"{row[col]}" for col in matching_columns]
                insert_values = [None if x == 'nan' else x for x in insert_values]
                auction_id = row["id"]
                value = ""
                for i, x in enumerate(insert_values):
                    if i != 0:
                        value += " , "
                    if x:
                        value += f"{insert_columns[i]} = {x}"
                    else:
                        value += f"{insert_columns[i]} = NULL"
                query = f"DELETE FROM crawling WHERE id IN (%s)"
                cursor.execute(query, (auction_id,))
            cursor.execute("commit;")
        
"""
for id_excel in ids_from_excel:    
ids_from_excel은 엑셀 파일에서 얻은 ID들의 리스트입니다.
엑셀 파일에서 각 ID를 하나씩 가져와서 반복합니다.

if id_excel in ids_from_db:
ids_from_db는 데이터베이스에서 얻은 ID들의 리스트입니다.
가져온 ID가 데이터베이스 ID 리스트에 존재하는지 확인합니다.

ids_be_delete.append(id_excel):
데이터베이스에서 삭제할 ID로 확인된 ID를 ids_be_delete 리스트에 추가합니다.
삭제될 ID들을 추적하기 위한 리스트입니다.

pd_be_delete = data.loc[df[id].isin(ids_be_delete)]:
data DataFrame에서 ids_be_delete 리스트에 있는 ID와 일치하는 행들을 선택합니다.
선택된 행들은 pd_be_delete DataFrame에 저장됩니다.

for i, row in pd_be_delete.iterrows()::
pd_be_delete DataFrame의 각 행에 대해 반복합니다.

insert_columns = [col for col in matching_columns]:
matching_columns에 정의된 컬럼들의 이름을 insert_columns 리스트에 저장합니다.

insert_values = [f"{row[col]}" for col in matching_columns]:
matching_columns에 정의된 컬럼들의 값을 insert_values 리스트에 저장합니다.

auction_id = row[id]:
현재 행에서 ID 값을 auction_id 변수에 저장합니다.

query = f"DELETE FROM crawling WHERE id IN {auction_id}":
삭제 쿼리문을 생성합니다. auction_id 값을 사용하여 WHERE 절에서 해당 ID를 지정합니다.

cursor.execute(query):
생성된 쿼리문을 실행하여 데이터베이스에서 해당 ID의 데이터를 삭제합니다.

cursor.execute("commit;"):
삭제 작업을 커밋하여 데이터베이스에 변경사항을 저장합니다."""