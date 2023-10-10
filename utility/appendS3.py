import os
import sys
import boto3
from dotenv import load_dotenv
from urllib.parse import quote
import pandas as pd
from .saveFile import createDirectory
from .saveFile import toJpg
from .saveFile import removeDirectory
import time
from datetime import datetime
import re 
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from defines.dataframe import dataframe as create_df


def main(df, temp = None):
    print("img -> s3 저장")
    load_dotenv()
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

    if temp == None:
        temp = create_df(None, None)
    else:
        temp = pd.DataFrame(temp)
        
    for auction_name in df.auction_name.unique():
        df_temp = df[df["auction_name"] == auction_name]
        # s3 저장을 위한 폴더명 정의
        company = df_temp["company"].unique()[0]
        transact_date = df_temp["transact_date"].unique()[0]
        if type(transact_date) == np.datetime64 :
            transact_date = str(transact_date).split('T')[0]
        if type(transact_date) == str:
            transact_date = datetime.strptime("-".join(re.split("/|-|\.", transact_date)), "%Y-%m-%d").date()

        transact_y = transact_date.year
        transact_m = transact_date.month
        # from datetime import datetime 
        # transact_date = datetime.strptime(df_temp["transact_date"].unique()[0], "%Y.%m.%d")
        # transact_y = transact_date.year
        # transact_m = transact_date.month
        print(transact_y, transact_m)

        directory = "{0}/{1}/{2}_{3}".format(
            int(transact_y), int(transact_m), company, auction_name.replace(':', '').replace('/', '-')
        ).strip()

        # s3에 폴더가 있는가?
        check = s3.list_objects(Bucket=BUCKET_NAME, Prefix=directory, MaxKeys=1)

        # 폴더가 없으면 s3저장을 위한 로컬 임시 폴더 생성
        if "Contents" not in check:
            print("s3 저장을 위한 임시 폴더 생성 : ", directory)
            createDirectory(directory)
        for lot, url in zip(df_temp["lot"], df_temp["img"]):
            if url:
                s3_path = "{0}/{1}.jpg".format(directory, lot)
                # 없을때 만 다음 코드 실행
                print(url, directory, lot)
                if "Contents" not in check:
                    # print(url)
                    toJpg(url, directory, lot)
                    time.sleep(2)
                    upload_file = open(s3_path, "rb")
                    s3.put_object(
                        Bucket=BUCKET_NAME,
                        Body=upload_file,
                        Key=s3_path,
                        ContentType="image/jpeg",
                        ACL="public-read",
                    )
                auction_url = "https://{bucket}.s3.{region}.amazonaws.com/{path}".format(
                    bucket=BUCKET_NAME, region=AWS_REGION, path=quote(s3_path)
                )
                df_temp.loc[df["lot"] == lot, "img"] = auction_url
                
            # 로컬 임시 폴더 삭제

        else:
            temp = pd.concat([temp, df_temp], ignore_index=True)
            # removeDirectory(directory)
    else:
        df = temp
    return df
