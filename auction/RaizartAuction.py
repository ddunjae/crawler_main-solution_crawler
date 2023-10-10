from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate
from defines.dataframe import dataframe as create_df
from defines.errmsg import err_msg


def Card(driver, url):
    df = create_df(
        [
            "lot",
            "img",
            "artist_kor",
            "artist_eng",
            "title_eng",
            "title_kor",
            "mfg_date",
            "material_kor",
            "material_eng",
            "material_kind",
            "height",
            "width",
            "depth",
            "description",
            "hammer_price",
            "selling_price",
            "start_price",
            "estimate_min",
            "estimate_max",
            "competition",
        ],
        dict,
    )
    driver.get(url + "&listmaxcount=100000")
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    auction_name = soup.find("div", class_="left left_cont").find("h2").text.strip()
    print(re.findall(
            "(?:.+경매마감: )(.+?</p>)",
            re.sub("\n", "", str(soup.find("div", class_="right")))
        )[0][:12])
    transact_date = datetime.strptime(
        re.findall(
            "(?:.+경매마감: )(.+?</p>)",
            re.sub("\n", "", str(soup.find("div", class_="right")))
        )[0][:12].strip(),"%Y. %m. %d")
    print(auction_name, transact_date)

    url_list = []
    for i in soup.findAll("div", class_="list-inner"):
        url_list.append(
            "https://www.raizart.co.kr"
            + i.find("div", class_="img-w").find("a").get("href")
        )
        lot = re.sub("[^0-9]", "", i.find("p", class_="lotNum").text)
        temp = str(i.find("div", class_="img-w").find("img"))
        if re.findall("(?:.+')(.+?')", temp):
            img = "https://www.raizart.co.kr" + quote(
                re.findall("(?:.+')(.+?')", temp)[0][:-1]
            )
        else:
            img = ""
        if i.find("span", class_="en_name").text.strip() == "Anonymous":
            artist_kor, artist_eng = "", ""
        else:
            artist_kor = Language("kor", i.find("span", class_="kr_name").text.strip())
            artist_eng = Language("eng", i.find("span", class_="en_name").text.strip())
            i.find("p", class_="name").span.extract()

        title_kor = Language("kor", i.find("span", class_="artwork_tlt").text.strip())
        title_eng = Language("eng", i.find("span", class_="artwork_tlt").text.strip())
        i.find("p", class_="txt").span.extract()

        w_info = re.sub("\t", "", i.find("p", class_="txt").text.strip()).split("\n")
        mfg_date, material_kor, material_eng = "", "", ""
        height, width, depth = "", "", ""
        description = []
        for txt in w_info:
            if not mfg_date:
                mfg_date = MfgDate(txt)
                if mfg_date:
                    continue
            if not (material_kor or material_eng):
                temp = Material(txt, txt, "")
                if temp != "Others" or temp != "Edition":
                    material_kor = Language("kor", txt)
                    material_eng = Language("eng", txt)
            if not (height or width or depth):
                size, etc = Size(txt)
                height = size["height"]
                width = size["width"]
                depth = size["depth"]
                if etc:
                    description.append(etc)

        price_list = i.find("div", class_="auction-info").findAll("dl")

        start_bid = re.sub("[^0-9]", "", price_list[1].text)
        estimate = price_list[2].text.split("~")
        estimate_min = re.sub("[^0-9]", "", estimate[0])
        estimate_max = re.sub("[^0-9]", "", estimate[1])
        winning_bid, selling_price, competition = "", "", ""
        if int(re.sub("[^0-9]", "", i.find("span", class_="now_bid_size").text)) != 0:
            winning_bid = re.sub("[^0-9]", "", i.find("b", class_="now_price").text)
            competition = (int(winning_bid) / int(start_bid)) - 1
            selling_price = int(winning_bid) * 1.165
        description = " / ".join(description)
        material_kind = Material(material_eng, material_kor, description)

        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_kor"].append(artist_kor)
        df["artist_eng"].append(artist_eng)
        df["title_kor"].append(title_kor)
        df["title_eng"].append(title_eng)
        df["mfg_date"].append(mfg_date)
        df["height"].append(height)
        df["width"].append(width)
        df["depth"].append(depth)
        df["material_kor"].append(material_kor)
        df["material_eng"].append(material_eng)
        df["material_kind"].append(material_kind)
        df["estimate_min"].append(estimate_min)
        df["estimate_max"].append(estimate_max)
        df["start_price"].append(start_bid)
        df["hammer_price"].append(winning_bid)
        df["selling_price"].append(selling_price)
        df["competition"].append(competition)
        df["description"].append(description)
    df = pd.DataFrame(df)
    df["auction_name"] = auction_name
    df["transact_date"] = transact_date

    return df, url_list

def Detail(driver, url_list):
    df = create_df(["lot", "artist_birth", "artist_death"], dict)
    for i in url_list:
        driver.get(i)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        lot = soup.find("p", class_="lot_tit").text.strip()
        artist_birth = ""
        artist_death = ""
        if soup.find("span", class_="year_info").text.strip() != "":
            artist_date = re.sub(
                "[^0-9-]",
                "",
                re.sub("~", "-", soup.find("span", class_="year_info").text),
            ).strip()
            date_parts = artist_date.split("-")
            if len(date_parts) == 2:
                artist_birth = date_parts[0]
                artist_death = date_parts[1]
            elif len(date_parts) == 1:
                artist_birth = date_parts[0]
            print(artist_birth, artist_death)    
        df["lot"].append(lot)
        df["artist_birth"].append(artist_birth)
        df["artist_death"].append(artist_death)

    return pd.DataFrame(df)


def login(driver):
    load_dotenv()
    print("라이즈아트옥션 접속 중...")
    driver.get("https://www.raizart.co.kr/?pn=member.login.form")
    print("라이즈아트옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@name='login_id']").send_keys(
        os.environ.get("auctionID2")
    )
    driver.find_element_by_xpath("//*[@name='login_password']").send_keys(
        os.environ.get("auctionPW2")
    )
    driver.find_element_by_xpath("//*[@class='login-btn']").click()


def logout(driver):
    driver.get("https://www.raizart.co.kr/program/member.login.pro.php?_mode=logout")


def main(driver, df):
    login(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    on_off = soup.find("div", {"id": "allmenu"}).findAll("ul", class_="allmenu-list")

    while True:
        auction_list = []
        check = False
        print("-" * 20)
        print("1 : Offline\n2 : Online\nq : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer == "1":
            for offline in on_off[0].findAll("li"):
                if "경매 준비중" in offline.text:
                    print(err_msg["no_auction"])
                    logout(driver)
                    return None, None
                if "지난경매결과" in offline.text:
                    break
                auction_list.append(
                    "https://www.raizart.co.kr" + offline.find("a").get("href")
                )
                check = True
            kind = "offline"
            break
        elif answer == "2":
            for offline in on_off[1].findAll("li"):
                if "경매 준비중" in offline.text:
                    print(err_msg["no_auction"])
                    return None, None
                if "지난경매결과" in offline.text:
                    break
                auction_list.append(
                    "https://www.raizart.co.kr" + offline.find("a").get("href")
                )
                check = True
            kind = "online"
            break
        elif answer == "3":
            url = input("url을 입력하세요 : ")
            auction_list.append(url)
            while True:
                kind = input("1 : offline\n2 : online\n번호를 입력하세요: ")
                if kind == "1":
                    kind = "offline"
                    break
                elif kind == "2":
                    kind = "online"
                    break
                else:
                    print(err_msg["no_option"])
                check = True
            break
        elif answer == "q":
            print("라이즈아트옥션 로그아웃 중...")
            logout(driver)
            return None, None
        else:
            print(err_msg["no_option"])
    df = create_df(None, None)
    for url in auction_list:
        df_card, url_list = Card(driver, url)
        df_detail = Detail(driver, url_list)
        df_temp = pd.merge(df_card, df_detail, how="outer", on="lot")
        df = pd.concat([df, df_temp], ignore_index=True)

    df["company"] = "라이즈아트옥션"
    df["on_off"] = kind
    df["currency"] = "KRW"
    df["location"] = "Korea"

    print("라이즈아트옥션 로그아웃 중...")
    logout(driver)

    return df, kind
