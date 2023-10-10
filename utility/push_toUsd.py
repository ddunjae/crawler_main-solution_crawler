import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import numpy as np
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.appendDB import connect_RDS
from defines.dataframe import dataframe as create_df


def cny_cnh(cny, cnh):
    if str(cnh).lower().strip() in ["nan", "none", ""] and cny:
        cnh = cny
    return cnh

def crawling_currency(driver, date):

    driver.get("http://www.smbs.biz/ExRate/TodayExRate.jsp")
    time.sleep(1)
    # driver.switch_to.alert.accept() #환율사이트에 알람이 뜰 때만 사용하게 해야함(공휴일, 주말)
    # time.sleep(1)
    driver.find_element_by_xpath("//button[@onclick='closePopupNotToday();']").click()
    time.sleep(1)
    base_df = create_df(
        ["date", "krw", "gbp", "eur", "cny", "cnh", "hkd", "sgd", "chf"], dict
    )
    # driver.quit()
    # date = datetime.strptime("1997-12-31", "%Y-%m-%d")
    date = date + timedelta(days=1)
    print(date)
    while date <= datetime.today():
    # while date <= datetime.strptime("1998-12-31", "%Y-%m-%d"):
        driver.find_element_by_xpath("//input[@id='searchDate']").click()
        driver.find_element_by_xpath("//input[@id='searchDate']").send_keys(
            Keys.BACKSPACE * 8
        )
        time.sleep(1)
        driver.find_element_by_xpath("//input[@id='searchDate']").send_keys(
            "{0}{1}{2}".format(
                date.year,
                date.month if date.month >= 10 else "0" + str(date.month),
                date.day if date.day >= 10 else "0" + str(date.day),
            )
        )
        time.sleep(1)
        driver.find_element_by_xpath(
             "/html/body/div/div[4]/div[2]/div/form/p[2]/a[2]/img"
        ).click()
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            al = driver.switch_to.alert
            al.accept()
        except:
            pass
        krw, gbp, eur, cny, cnh, hkd, sgd, chf = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        standard_krw_list = soup.find_all("tbody")[1].find_all("tr")
        for standard_krw in standard_krw_list:
            if "USD" in standard_krw.find_all("td")[0].text:
                usd_to_krw = re.sub("[^0-9.]", "", standard_krw.find_all("td")[1].text)
                if usd_to_krw:
                    krw = 1 / float(usd_to_krw)
            elif "CNH" in standard_krw.find_all("td")[0].text:
                cnh_to_krw = re.sub("[^0-9.]", "", standard_krw.find_all("td")[1].text)
                if cnh_to_krw and usd_to_krw:
                    cnh = float(cnh_to_krw) / float(usd_to_krw)
        currency_list = soup.find_all("tbody")[2].find_all("tr")
        for currency in currency_list:
            for key in ["GBP", "EUR", "CNY", "CNH", "HKD", "SGD", "CHF"]:
                if key in currency.find_all("td")[0].text:
                    if key in ["GBP", "EUR"]:
                        exec("{0}= re.sub('[^0-9.]', '', currency.find_all('td')[3].text)".format(key.lower()))
                    else:
                        temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                        if temp:
                            exec("{0} = 1 / float(temp)".format(key.lower()))






            if "GBP" in currency.find_all("td")[0].text:
                gbp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
            if "EUR" in currency.find_all("td")[0].text:
                eur = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
            if "CNY" in currency.find_all("td")[0].text:
                temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                if temp:
                    cny = 1 / float(temp)
            if "CNH" in currency.find_all("td")[0].text:
                temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                if temp:
                    cnh = 1 / float(temp)
            if "HKD" in currency.find_all("td")[0].text:
                temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                if temp:
                    hkd = 1 / float(temp)
            if "SGD" in currency.find_all("td")[0].text:
                temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                if temp:
                    sgd = 1 / float(temp)
            if "CHF" in currency.find_all("td")[0].text:
                temp = re.sub("[^0-9.]", "", currency.find_all("td")[3].text)
                if temp:
                    chf = 1 / float(temp)
        print(date, gbp, eur, cny, cnh, hkd, sgd, chf, krw)
        base_df["date"].append(("{0}-{1}-{2}".format(date.year, date.month, date.day)))
        base_df["krw"].append(krw)
        base_df["gbp"].append(gbp)
        base_df["eur"].append(eur)
        base_df["cny"].append(cny)
        base_df["cnh"].append(cnh)
        base_df["hkd"].append(hkd)
        base_df["sgd"].append(sgd)
        base_df["chf"].append(chf)
        date = date + timedelta(days=1)
    df = pd.DataFrame(base_df)
    df["cnh"] = df.apply(lambda x: cny_cnh( x.cny, x.cnh), axis=1)
    df = df[["date", "krw", "gbp", "eur", "cnh", "hkd", "sgd", "chf"]]
    return df


    



def push_usd(driver):
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
            connect_args={'charset':'utf8'}
        )


        check = pd.read_sql("select date from to_usd order by date desc limit 1", conn)
        date = check["date"].unique()[0]
        date = datetime(date.year, date.month, date.day)
        conn.close()
        today = datetime.today()
        if date == datetime(today.year, today.month, today.day):
            return
        print(date, datetime.today())
        df = crawling_currency(driver, date)
        try:
            df.to_sql(
                name="to_usd", con=engine, if_exists="append", index=False
            )
        except Exception as e:
            print(e)
        print("update 'to_usd'")


def get_usd():
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
            + database
           ,
           connect_args={'charset':'utf8'}
        )

        df = pd.read_sql("select * from to_usd order by date desc", conn)
        return df
