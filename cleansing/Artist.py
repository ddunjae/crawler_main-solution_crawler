import pandas as pd
import pymysql
import os
import sys
from sshtunnel import SSHTunnelForwarder
# DB 연결
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


        query = """
        UPDATE solution_yeolmae.need_cleansing_data AS c
        INNER JOIN solution_yeolmae.artist AS a ON c.artist_kor = a.name_kr
                                            AND c.artist_birth = a.born
                                            AND c.artist_death = a.dead
        SET c.artist_id = a.id,
            c.artist_birth = a.born,
            c.artist_death = a.dead
        """
        artist_bio = pd.read_sql(query, conn) #db에 적용
        
        show_excel = pd.read_sql(query,conn) #엑셀로 보여지게
        base_url = "/Users/hanseungjae/auction_solution/artist_bio/"
        show_excel.to_excel(base_url+"artist_bio_0609_1.xlsx", index=False)
        def names_list(names):
            if names:
                return names.split(";")
            else:
                return[]
        artist_bio["alias_kr"] = artist_bio.apply(lambda x : list(map(lambda y : re.sub(" ", "", y).lower(), names_list(x.alias_kr))), axis = 1)
        artist_bio["alias_en"] = artist_bio.apply(lambda x : list(map(lambda y : re.sub(" ", "", y).lower(), names_list(x.alias_en))), axis = 1)
        print
        conn.close()
            
def Artist(kor, eng, born, dead):
    artist_id = None
    check_kor, check_eng = True, True
    if type(kor) == str and kor.strip() != "":
        kor_ = re.sub(" ","", kor).lower()
        
        kor_filter = artist_bio.apply( lambda x : x.alias_kr.__contains__(kor_) , axis = 1)
    else:
        kor_filter = pd.Series([True]*len(artist_bio))
        check_kor = False
    if type(eng) == str and eng.strip() != "":
        eng_ = re.sub(" ","", eng).lower()
        
        eng_filter = artist_bio.apply( lambda x : x.alias_en.__contains__(eng_) , axis = 1)
    else:
        eng_filter = pd.Series([True]*len(artist_bio))
        check_eng = False

    if not(check_kor or check_eng):
        return kor, eng, born, dead, artist_id
    
    if str(born).strip() not in ["None", "nan", ""]:
        born_filter = artist_bio.apply( lambda x : float(x.born) == float(born), axis = 1)
    else:
        born_filter = pd.Series([True]*len(artist_bio))
    if len(artist_bio[kor_filter & eng_filter & born_filter]) > 0:
        artist_id = artist_bio["id"][kor_filter & eng_filter & born_filter].iloc[0]
        kor = artist_bio["name_kr"][kor_filter & eng_filter & born_filter].iloc[0]
        eng = artist_bio["name_en"][kor_filter & eng_filter & born_filter].iloc[0]
        born = artist_bio["born"][kor_filter & eng_filter & born_filter].iloc[0]
        dead = artist_bio["dead"][kor_filter & eng_filter & born_filter].iloc[0]
        # print(kor, eng, born, dead, artist_id)

    return kor, eng, born, dead, artist_id