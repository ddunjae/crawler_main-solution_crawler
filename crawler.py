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
import numpy as np
import re

from defines.dataframe import dataframe as create_df
from cleansing.CanvasSize import CanvasSize
from defines.dataframe import dataframe as create_df
import utility.appendS3 as appendS3
import utility.appendDB as appendDB
import utility.saveFile as saveFile
from utility.openDriver import open_driver
from utility.push_toUsd import push_usd
from cleansing.AuctionResult import auction_result
import cleansing.exchangeRate as exchangeRate
from defines.errmsg import err_msg


driver, exchangeRate_driver = open_driver()
push_usd(exchangeRate_driver)
auctions = [
    "KAuction",
    "SeoulAuction",
    "ToartAuction",
    "AAuction", 
    "artdayAuction",
    "IAuction", 
    "MyartAuction",
    "RaizartAuction",
    "KanAuction",
]
select_option = "\n\n" + "-" * 20 + "\n"
for auction, index in zip(auctions, range(len(auctions))):
    select_option += "{0} : {1}\n".format(index, auction)
select_option += "\nq : 종료\n" + "-" * 20 + "\n"
while True:
    df = create_df(None, None)
    print(select_option)
    answer = input("크롤링 할 사이트 번호를 입력하시오 : ")
    if answer == "q":
        print("프로그램 종료")
        driver.quit()
        exchangeRate_driver.quit()
        quit()
    if answer.isdigit():
        if int(answer) < len(auctions):
            auction_name = auctions[int(answer)]
        else:
            print(err_msg["no_option"])
            continue
    else:
        print(err_msg["no_option"])
        continue
    auc = __import__("auction.{0}".format(auction_name), fromlist=[auction_name])
    df, kinds = auc.main(driver, df)
    if df is None:
        continue

    directory = os.path.dirname(os.path.realpath(__file__)) + "/crawling_data"
    filename = "/{0}_{1}_{2}.xlsx".format(
        auction_name, kinds, str(datetime.now().strftime("%y%m%d_%H%M"))
    )

    saveFile.toExcel(df, directory, filename)
    df = df.replace("", np.NaN)
    df["size_table"] = df.apply(
        lambda x: CanvasSize(x.material_kind, x.height, x.width, x.description), axis=1
    )
    df["location"] = df.apply(lambda x : 'Hong Kong' if re.findall('홍콩|hongkong|hong kong', x.auction_name.lower()) else 'Korea' , axis = 1)
    df["bid_class"],df["competition"] = zip(*df.apply(lambda x : auction_result(winning_bid = x.hammer_price, start_bid = x.start_price, estimate_min = x.estimate_min, estimate_max = x.estimate_max), axis = 1))

    df["usd_hammer_price"],df["usd_start_price"],df["usd_selling_price"],df["usd_estimate_min"],df["usd_estimate_max"] = zip(*df.apply(lambda x : exchangeRate.exchange(x.transact_date, x.currency, x.hammer_price, x.start_price, x.selling_price, x.estimate_min, x.estimate_max), axis = 1))
    df = df.replace("", np.NaN)
    print("엑셀파일로 저장합니다.")
    saveFile.toExcel(df, directory, filename)
    df = appendS3.main(df)
    print("엑셀파일로 저장합니다.")
    saveFile.toExcel(df, directory, filename)

    appendDB.main(df)
