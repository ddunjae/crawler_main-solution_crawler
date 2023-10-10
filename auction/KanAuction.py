from cmath import nan
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.CanvasSize import CanvasSize
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate
from defines.dataframe import dataframe as create_df

from utility.openDriver import open_driver


def past(driver, fromdate, isCrawlFromDate = None):
    df = create_df(["company","img", "lot", "auction_name", "transact_date", "artist_kor", "artist_eng", "title_kor", "title_eng", "mfg_date","height", "width", "depth", "material_kind", "material_kor", "material_eng","currency", "hammer_price","estimate_min", "estimate_max", "description"], dict)
    page = 384
    check = False

    if isCrawlFromDate:
        page = 1

    while True:
        driver.get("http://www.kanauction.kr/auction/past/main?page={0}".format(page))
        print(page)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if not soup.find("div", class_= "auctionGate").find_all("ul", class_="article") or check:
            break
        for li in soup.find("div", class_= "auctionGate").find_all("ul", class_="article"):
            transact_date = datetime.strptime(li.find("span", class_="aucDate").text , "%Y.%m.%d").date()
            if transact_date < fromdate: # 2023.05.26 &
                check = True
                break
            # print(li.find("span", class_= "lot").text)
            transact_date = datetime.strptime(str(transact_date), "%Y-%m-%d")
            desc = re.sub("\t|\n", " ",li.find("span", class_= "aucTitle").text).strip()
            desc_split = desc.split("|")
            title = desc_split[0]
            if "출품" in title and  "취소" in title:
                continue
            df["company"].append('칸옥션')   # 출품처
            df["title_kor"].append(Language("kor", title))
            df["title_eng"].append(Language("eng", title))
            df["description"].append(desc)
            df["transact_date"].append(transact_date)
            df["img"].append("http://www.kanauction.kr" + li.find("div", class_= "thumbImg").find("img").get("src"))
            df["lot"].append(int(re.sub("[^0-9]", "", li.find("span", class_= "lot").text)))
            df["auction_name"].append(li.find("li", class_="info breakWord").text.split("|")[1].strip())
            artist = li.find("span", class_="title").text
            df["artist_kor"].append(Language("kor", artist))
            df["artist_eng"].append(Language("eng", artist))
            estimate = li.find_all("span", class_="price")[0].text.split("-")
            currency, hammer_price = None, None
            if "별도문의" in re.sub(" ", "",estimate[0]):
                df["estimate_min"].append(None)
                df["estimate_max"].append(None)
            else:
                currency = li.find("span", class_="price").find("span").text
                df["estimate_min"].append(re.sub("[^0-9]", "", estimate[0]))
                if len(estimate) > 1:
                    df["estimate_max"].append(re.sub("[^0-9]", "", estimate[1]))
                else:
                    df["estimate_max"].append(None)
            if len(li.find_all("span", class_="price")) > 1:
                if currency == None:
                    currency = li.find_all("span", class_="price")[1].find("span").text
                # print(li.find_all("span", class_="price")[1].text)
                hammer_price = re.sub("[^0-9]", "", li.find_all("span", class_="price")[1].text)
            df["hammer_price"].append(hammer_price) 
            df["currency"].append(currency)      
            
            mfg_date, material_kind, material_kor, material_eng = None, None, None, None
            size = {"height":None, "width":None, "depth":None}
            for d in desc_split[1:]:
                if re.search("\d\d\d\d|세기", d) and not mfg_date:
                    mfg_date = MfgDate(d)
                elif ("㎝" in d or "cm" in d.lower()) and not (size["height"] or size["width"] or size["depth"]):
                    size,_ = Size(d)
                    print(size)
                    break
                elif not (size["height"] or size["width"] or size["depth"]):
                    material_kind = Material(d, d, desc)
                    material_kor = Language("kor", d)
                    material_eng = Language("eng", d)

            
            df["mfg_date"].append(mfg_date)
            df["height"].append(size["height"])
            df["width"].append(size["width"])
            df["depth"].append(size["depth"])
            df["material_kind"].append(material_kind)
            df["material_kor"].append(material_kor)
            df["material_eng"].append(material_eng)

        # temp = pd.DataFrame(df)
        # temp.to_excel("crawling_data/KanAuction_past.xlsx", index=False)
        page += 1
        
    df = pd.DataFrame(df)
    df["location"] = "Korea"
    df["on_off"] = "offline"
    df['start_price'] = ''
    df['selling_price'] = ''
    # df.to_excel("crawling_data/KanAuction_past.xlsx", index=False)
    return df, "offline"

def main(driver, df):
    while True:
        print("-" * 20)
        print(
            "1 : proceeding\n2 : past\n\nq : 뒤로가기"
        )
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer == "1":
            driver.get("http://www.kanauction.kr/auction/going/main")
            print("칸옥션 진행중인 경매 크롤러 만들어야 합니다.")
            continue
        if answer == "2":
            driver.get("http://www.kanauction.kr/auction/past/main")
            while True:
                fromdate = input("Please enter the from date (YYYY.MM.DD) / or cancel is 'q' : ")
                if fromdate == "q":
                    return None, None
                try:
                    fromdate = datetime.strptime(fromdate, "%Y.%m.%d").date()
                    return past(driver, fromdate, True)
                    
                    # break
                except:
                    print("날짜를 제대로 입력해주세요.")
                
        elif answer == "q":
            return None, None
        else:
            print("보기의 번호를 제대로 입력해주세요.")
            continue
        break


driver, exchangeRate_driver = open_driver()
past(driver, datetime.strptime("2015.01.01", "%Y.%m.%d").date())
