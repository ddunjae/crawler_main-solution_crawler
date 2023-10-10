from cmath import nan
from types import NoneType
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


# 국문데이터 수집
def Card(_driver, url):
    url_list = []
    _driver.get(url)
    
    try:
        WebDriverWait(_driver, 3).until(EC.alert_is_present())
        al = _driver.switch_to.alert
        al.accept()
        print("진행중인 경매가 없습니다.")
        return None
    except:
        df = create_df(["lot","hammer_price", "selling_price", "start_price", "estimate_min", "estimate_max", "competition"], dict)
        print("데이터 수집 중...")
        check = False
        for p in range(1, 100):
            if "?" in url:
                _driver.get(url + "&page=" + str(p))
            else:
                _driver.get(url + "?page=" + str(p))
            time.sleep(1)
            html = _driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
            soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
            for i in soup.find_all("ul", class_="gall_con"):
                if i.find("a").get("href") in url_list:
                    check = True
                    break
                url_list.append(i.find("li", class_="gall_num").find("a").get("href"))
                df["lot"].append(i.find("li", class_="gall_num").find("a").text)
                price = re.sub("\n", "", str(i.find("li", class_="auction_price")))
                try:
                    if int(i.find("li", class_="auction_num").text[6:-1]) > 0:
                        winning_bid = re.sub(
                            "[^0-9]",
                            "",
                            re.findall("(?:.+현재가)(?:.+KRW)(.+?</span>)", price)[0],
                        )
                        selling_price = int(winning_bid) * 1.165
                    else:
                        winning_bid, selling_price = nan, nan
                except:
                    if "낙찰가" in i.find("li", class_="auction_num").text:
                        winning_bid = re.sub(
                            "[^0-9]",
                            "",
                            i.find("li", class_="auction_num").text.split(")")[1],
                        )
                        selling_price = int(winning_bid) * 1.165
                    else:
                        winning_bid, selling_price = nan, nan
                if re.findall("(?:.+시작가)(?:.+KRW)(.+?</span>)", price):
                    start_bid = re.sub(
                        "[^0-9]",
                        "",
                        re.findall("(?:.+시작가)(?:.+KRW)(.+?</span>)", price)[0],
                    )
                else:
                    start_bid = nan
                if re.findall("(?:.+추정가)(.+?</li>)", price):
                    estimate = re.sub(
                        "[^0-9~]", "", re.findall("(?:.+추정가)(.+?</li>)", price)[0]
                    ).split("~")
                    estimate_min, estimate_max = estimate[0], estimate[1]
                else:
                    estimate_min, estimate_max = nan, nan
                if type(winning_bid) != float and type(start_bid) != float:
                    competition = (int(winning_bid) / int(start_bid)) - 1
                else:
                    competition = nan
                df["hammer_price"].append(winning_bid)
                df["selling_price"].append(selling_price)
                df["start_price"].append(start_bid)
                df["estimate_min"].append(estimate_min)
                df["estimate_max"].append(estimate_max)
                df["competition"].append(competition)


            if check:
                auction_name = soup.find("div", class_="fl").text
                transactDate = re.findall(
                    "(?:.+경매종료일</span>)(.+?일)",
                    re.sub("\n", "", str(soup.find("div", {"id": "ongoing_text"}))),
                )[0]
                transactDate = datetime.strptime(transactDate.strip(), "%Y년 %m월 %d일")
                break
        df = pd.DataFrame(df)
        # 경매명
        df["auction_name"] = auction_name
        # 거래년도
        df["transact_date"] = transactDate
        return df, url_list

def Detail(driver, url_list):
    df = create_df(["lot", "img", "artist_kor", "artist_eng", "title_kor", "title_eng", "material_kor", "material_eng", "material_kind", "description", "height", "width", "depth", "mfg_date"], dict)
    for url in url_list:
        description = []
        driver.get("https://toartauction.com/auction/" + url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        lot = soup.find("li", class_= "auction_view_title").text[4:]
        img = "https://toartauction.com" + quote(
            soup.find("img", class_="view-img").get("orig_src")
        )
        artist = soup.find_all("li", class_="auction_view_title").pop().text
        if re.search("[ㄱ-ㅣ가-힣]", artist) is None:
            artist_kor, artist_eng = "", artist
        else:
            artist_kor, artist_eng = artist, ""
        title = soup.find("li", class_="auction_view_title2").text
        if re.search("[ㄱ-ㅣ가-힣]", title) is None:
            title_kor, title_eng = "", title
        else:
            title_kor, title_eng = title, ""
        msy = soup.find("ul", class_="auction_subject").find_all("li")
        if re.search("[ㄱ-ㅣ가-힣]", msy[0].text) is not None:
            material_kor, material_eng = msy[0].text.strip(), ""
        elif msy[0].text.strip() == "":
            material_eng, material_kor = "", ""
        else:
            material_kor, material_eng = "", msy[0].text.strip()

        mfg_date = MfgDate(msy[1].text)
        size, etc = Size(msy[1].text)
        height = size["height"]
        width = size["width"]
        depth = size["depth"]
        if re.sub("/", "", etc) != "":
            description.append(etc)
        material_kind = Material(material_eng, material_kor, description)
        description = "\n".join(description)
        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_kor"].append(artist_kor)
        df["artist_eng"].append(artist_eng)
        df["title_kor"].append(title_kor)
        df["title_eng"].append(title_eng)
        df["material_kor"].append(material_kor)
        df["material_eng"].append(material_eng)
        df["material_kind"].append(material_kind)
        df["description"].append(description)
        df["height"].append(height)
        df["width"].append(width)
        df["depth"].append(depth)
        df["mfg_date"].append(mfg_date)
    return pd.DataFrame(df)



def login(driver):
    load_dotenv()
    print("토탈아트옥션 접속 중...")
    driver.get("https://toartauction.com/member/login.html")
    html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
    soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정

    print("토탈아트옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@name='login_id']").send_keys(
        os.environ.get("auctionID2")
    )
    driver.find_element_by_xpath("//*[@name='login_pw']").send_keys(
        os.environ.get("auctionPW2")
    )
    driver.find_element_by_xpath(
        "//*[@class='secession_btn secession_btn2 oh']"
    ).click()


def logout(driver):
    driver.get("https://toartauction.com/member/login.html")


def main(driver, df):
    login(driver)

    html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
    soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정

    while True:
        print("-" * 20)
        print("1 : online\n2 : url직접입력\nq : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")

        if answer == "1":
            url = "https://toartauction.com/" + soup.find("li", class_="m1").find(
                "a"
            ).get("href")
            break

        if answer == "2":
            url = input("url입력하세요 : ")
            break
        elif answer == "q":
            logout(driver)
            return None, None
        else:
            print("보기의 번호를 제대로 입력해주세요.")

    driver.get(url)
    
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        al = driver.switch_to.alert
        al.accept()
        print("진행중인 경매가 없습니다.")
        return None, None
    except:
        df_card, url_list = Card(driver, url)
        if df_card is None:
            return None, None
        df_detail = Detail(driver, url_list)
        df = pd.merge(df_card, df_detail, how="outer", on="lot")
        df["company"] = "토탈아트옥션"  # 출품처
        df["on_off"] = "online"  # 온라인/오프라인 구분
        df["currency"] = "KRW"
        
        print("데이터 수집을 완료했습니다.")
        # 로그아웃
        logout(driver)
        return df, ""
