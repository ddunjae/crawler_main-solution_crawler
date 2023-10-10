from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import os
import time
from urllib.parse import quote
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate
from defines.dataframe import dataframe as create_df
from defines.errmsg import err_msg


def Card(driver):
    df = create_df(
        [
            "lot",
            "img",
            "artist_kor",
            "artist_eng",
            "artist_birth",
            "artist_death",
            "title_kor",
            "title_eng",
            "height",
            "width",
            "depth",
            "material_kor",
            "material_eng",
            "material_kind",
            "mfg_date",
            "hammer_price",
            "selling_price",
            "estimate_min",
            "estimate_max",
            "competition",
            "description",
        ],
        dict,
    )
    url = driver.current_url
    url_list = []
    page = 0
    count = 1
    while 1:
        page += 1
        driver.get("{0}?&page={1}".format(url, page))
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if not soup.find("div", class_="table-body").find("tbody").find("tr"):
            break
        for tr in soup.find("div", class_="table-body").find("tbody").find_all("tr"):
            _description = []
            td = tr.find_all("td")
            lot = td[0].text.strip()
            # print(count, td[0].text.strip(), len(df["lot"]))
            count += 1
            img = "http://www.artday.co.kr" + quote(td[1].find("img").get("src"))
            url_list.append(
                "http://www.artday.co.kr/pages/auction/" + td[1].find("a").get("href")
            )
            artist = td[2].find_all("p")
            if artist[0].text.strip() not in ["", "작자미상"]:
                artist_kor = artist[0].text.strip()
            else:
                artist_kor = ""
            if artist[1].text.strip().lower() not in ["", "anonymous"]:
                artist_eng = artist[1].text.strip()
            else:
                artist_eng = ""
            if re.match("\d{4}", artist[2].text.strip()):
                artist_date = re.findall("\d{4}", artist[2].text)
                artist_birth = artist_date[0]
                if len(artist_date) > 1:
                    artist_death = artist_date[-1]
                else:artist_death=""
            else:
                artist_birth, artist_death = "",""
            work = td[3].find_all("p")
            for i in re.findall("(아트상품|\d+\s*점|사후판화)", work[0].text):
                _description.append(i)
            if re.findall(
                "[ㄱ-ㅣ가-힣]", re.sub("아트상품|\d+\s*점|사후판화|\(.*\)", "", work[0].text)
            ):
                title_kor = work[0].text.strip()
                title_eng = ""
            else:
                title_eng = work[0].text.strip()
                title_kor = ""
            height, width, depth = "", "", ""
            if work[1].text.strip() != "":
                size, etc = Size(work[1].text.strip())
                height = size["height"]
                width = size["width"]
                depth = size["depth"]
                if etc:
                    _description.append(etc)
            material_kor, material_kind, material_eng = "", "", ""
            if work[2].text.strip() != "":
                if "(" in work[2].text:
                    _description.append(work[2].text[work[2].text.index("(") :])
                    material = work[2].text[: work[2].text.index("(")]
                else:
                    material = work[2].text
                if re.search("[ㄱ-ㅣ가-힣]", material):
                    material_kor = material
                else:
                    material_eng = material

            mfg_date = MfgDate(work[3].text.strip())
            description = " / ".join(_description)
            material_kind = Material(material_kor, material_eng, description)
            estimate_min, estimate_max, winning_bid, selling_price, competition = (
                "",
                "",
                "",
                "",
                "",
            )
            if re.sub("[^0-9.]", "", td[5].text) != "":
                estimate = td[5].text.split("~")
                estimate_min = re.sub("[^0-9]", "", estimate[0])
                estimate_max = re.sub("[^0-9]", "", estimate[1])
            if re.sub("^[0-9.]", "", td[7].text) not in ["", "0"]:
                winning_bid = re.sub("[^0-9]", "", td[4].text)
                if winning_bid != "":
                    selling_price = int(winning_bid) * 1.165
                    if estimate_min and estimate_min == "0":
                        competition = int(winning_bid) / int(estimate_min) - 1
                    elif estimate_min == "0":
                        competition = int(winning_bid) / 50000
            df["lot"].append(lot)
            df["img"].append(img)
            df["artist_kor"].append(artist_kor)
            df["artist_eng"].append(artist_eng)
            df["artist_birth"].append(artist_birth)
            df["artist_death"].append(artist_death)
            df["title_kor"].append(title_kor)
            df["title_eng"].append(title_eng)
            df["height"].append(height)
            df["width"].append(width)
            df["depth"].append(depth)
            df["material_kor"].append(material_kor)
            df["material_eng"].append(material_eng)
            df["material_kind"].append(material_kind)
            df["mfg_date"].append(mfg_date)
            df["hammer_price"].append(winning_bid)
            df["selling_price"].append(selling_price)
            df["estimate_min"].append(estimate_min)
            df["estimate_max"].append(estimate_max)
            df["competition"].append(competition)
            df["description"].append(description)

    print(len(df["lot"]))
    return pd.DataFrame(df), url_list


def Detail(driver, url_list):
    df = create_df(
        ["lot", "hammer_price", "start_price", "selling_price", "competition"], dict
    )
    for detail in url_list:
        driver.get(detail)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        lot = soup.find("div", class_="goods-info").find("h2").text.strip()
        temp = soup.find("div", class_="goods-value").find_all("p")[1]
        winning_bid, selling_price = "", ""
        start_bid = re.sub("[^0-9]", "", temp.text.split("(")[1])
        competition = ""
        if (start_bid != "") and re.sub(
            "[^0-9]", "", soup.find("div", class_="goods-value").find("p").text
        ) != "0":
            winning_bid = re.sub("[^0-9]", "", temp.text.split("(")[0])
            selling_price = int(winning_bid) * 1.165
            competition = (int(winning_bid) / int(start_bid)) - 1
        df["lot"].append(lot)
        df["hammer_price"].append(winning_bid)
        df["start_price"].append(start_bid)
        df["selling_price"].append(selling_price)
        df["competition"].append(competition)
    return pd.DataFrame(df)


def main(driver, df):
    print("\n헤럴드아트데이옥션 접속 중...")
    driver.get("http://www.artday.co.kr/?")
    time.sleep(3)
    html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
    soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
    auction_kind = ["online", "offline"]
    while True:
        print("-" * 20)
        for kind, index in zip(auction_kind, range(len(auction_kind))):
            print("{0} : {1}".format(index, kind))
        print("{0} : 직접입력\nq : 뒤로가기".format(len(auction_kind)))
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer.isdigit():
            if int(answer) < len(auction_kind):
                if (
                    soup.find(class_="sub-nav-list")
                    .find_all("span")[int(answer)]
                    .find("a")
                    .get("href")
                    != "javascript:alert('준비중입니다.');"
                ):
                    url = "http://www.artday.co.kr" + (
                        soup.find(class_="sub-nav-list")
                        .find_all("span")[int(answer)]
                        .find("a")
                    ).get("href")
                    kind = auction_kind[int(answer)]
                    break
                else:
                    print(err_msg["no_auction"])
            elif int(answer) == len(auction_kind):
                sub_answer_url = input("url을 입력하세요 : ")
                while True:
                    sub_answer = input(
                        "0 : online\n1 : offline\nq : 뒤로가기\n번호를 입력하세요 : "
                    )
                    if sub_answer == "q":
                        break
                    if int(sub_answer) < len(auction_kind):
                        url = sub_answer_url
                        kind = auction_kind[int(sub_answer)]
                        break
                if sub_answer == "q":
                    continue
                else:
                    break
            else:
                print(err_msg["no_auction"])
                continue
        elif answer == "q":
            return None, None
        else:
            print(err_msg["no_option"])
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    if soup.find("h3", class_="auc-top-title"):
        auction_name = soup.find("h3", class_="auc-top-title").text
    else:
        auction_name = soup.find("div", class_="content-title").find("h3").text.strip()
    if kind == "offline":
        transact = (
            soup.find("div", class_="auction-info").find_all("p")[0].text.split(" ")[1]
        )
    else:
        transact = (
            soup.find("div", class_="auction-info").find_all("p")[1].text.split(" ")[1]
        )
    transactDate = ".".join(transact.split(".")[:3])

    df, url_list = Card(driver)
    if kind == "online":
        df = df.drop(["hammer_price", "selling_price", "competition"], axis=1)
        df_detail = Detail(driver, url_list)
        df = pd.merge(df, df_detail, how="outer", on="lot")
    df["transact_date"] = datetime.strptime(transactDate, ("%Y.%m.%d"))
    df["auction_name"] = auction_name
    df["company"] = "아트데이옥션"
    df["on_off"] = kind
    df["currency"] = "KRW"
    df["location"] = "Korea"
    print(df["auction_name"])
    # 끝나면 브라우져 닫기
    print("데이터 수집을 완료했습니다.")
    return df, kind
