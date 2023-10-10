import pandas as pd
import platform
from selenium import webdriver
import os
from datetime import datetime
from datetime import date
import sys
import os
import requests
import base64
import pymysql
import numpy as np
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.push_toUsd import get_usd
import re

usd_table = get_usd()

def exchange(transact_date, currency, hammer_price, start_price, selling_price, estimate_min, estimate_max):

    
    if type(transact_date) == np.datetime64 :
        transact_date = str(transact_date).split('T')[0]
    if type(transact_date) == str:
        transact_date = datetime.strptime("-".join(re.split("/|-|\.", transact_date)), "%Y-%m-%d").date()
    else: transact_date = transact_date.date()
    usd_hammer_price, usd_start_price, usd_selling_price, usd_estimate_min, usd_estimate_max = None, None, None, None, None
    
    if str(currency) not in ["", "nan", "None"]:
        if  len(usd_table[currency.lower()][usd_table["date"] == transact_date]) == 1:
            rate = usd_table[currency.lower()][usd_table["date"] == transact_date].iloc[0]
        else:
            rate = usd_table[currency.lower()].iloc[0]
        print(rate)
        # usd_table
        if str(hammer_price) not in ["", "nan", "None"]:
            usd_hammer_price = float(float(hammer_price) * float(rate))
        if str(start_price) not in ["", "nan", "None"]:
            usd_start_price = float(float(start_price) * float(rate))
        if str(selling_price) not in ["", "nan", "None"]:
            usd_selling_price = float(float(selling_price) * float(rate))
        if str(estimate_min) not in ["", "nan", "None"]:
            usd_estimate_min = float(float(estimate_min) * float(rate))
        if str(estimate_max) not in ["", "nan", "None"]:
            usd_estimate_max = float(float(estimate_max) * float(rate))
            print(usd_hammer_price, usd_start_price, usd_selling_price, usd_estimate_min, usd_estimate_max )
    return usd_hammer_price, usd_start_price, usd_selling_price, usd_estimate_min, usd_estimate_max 
        
        


    


# def main(driver2, df):
    
#     currency = df["currency"].unique()[0]
    
#     if str(currency) in ["nan", "None", ""]:
#         currency = "KRW"
#     driver2.get("https://www.google.com/search?q={0}+USD".format(currency))
#     print("{0} -> USD :".format(currency), end=" ", flush=True)
#     soup = BeautifulSoup(driver2.page_source, "html.parser")
#     usd = float(soup.find("div", {
#                 "id": "knowledge-currency__updatable-data-column"}).find("span", class_="DFlfde SwHCTb").text)
#     print("{0} $".format(usd))

#     df['usd_start_price'] = df.apply(
#         lambda x: int(x.start_bid) * usd if not pd.isnull(x.start_bid) else x.start_bid, axis=1)
#     df['usd_winning_bid'] = df.apply(
#         lambda x: int(x.winning_bid) * usd if not pd.isnull(x.winning_bid) else x.winning_bid, axis=1)
#     df['usd_selling_price'] = df.apply(
#         lambda x: int(x.selling_price) * usd if not pd.isnull(x.selling_price) else x.selling_price, axis=1)
#     df['usd_estimate_min'] = df.apply(
#         lambda x: int(x.estimate_min) * usd if not pd.isnull(x.estimate_min) else x.estimate_min, axis=1)
#     df['usd_estimate_max'] = df.apply(
#         lambda x: int(x.estimate_max) * usd if not pd.isnull(x.estimate_max) else x.estimate_max, axis=1)

#     return df
