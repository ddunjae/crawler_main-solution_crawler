from cmath import nan
from types import NoneType
from bs4 import BeautifulSoup
from numpy import nancumprod
import pandas as pd
from datetime import datetime
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate


def Card(driver, lang):
    print("데이터 수집중 (카드페이지)")
    df = {
        "lot": [],
        "img": [],
        "artist_" + lang: [],
        "title_" + lang: [],
        "material_kor": [],
        "material_eng": [],
        "height": [],
        "width": [],
        "depth": [],
        "mfg_date": [],
        "desc_card": [],
        "currency": [],
        "estimate_min": [],
        "estimate_max": [],
        "start_price": [],
        "hammer_price": [],
        "competition": [],
    }
    url = driver.current_url
    detail_url = []
    for page in range(1, 100):
        driver.get("{0}?page={1}".format(url, page))
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if not soup.find("ul", class_="product-list").find_all("li"):
            break
        for item in soup.find("ul", class_="product-list").find_all("li"):
            if item.find("i", class_="icon-cancle_box"):  # 출품취소
                continue
            (
                lot,
                img,
                artist,
                title,
                material_kor,
                material_eng,
                height,
                width,
                depth,
                mfg_date,
                desc_card,
            ) = ("", "", "", "", "", "", "", "", "", "", "")
            currency , estimate_min, estimate_max, start_bid, winning_bid, competition = (
                "",
                "",
                "",
                "",
                "",
                ""
            )
            lot = item.find("div", class_="num_heart-box").find("span").text
            img = re.sub("list/", "detail/", item.find("img").get("src"))
            artist = item.find("div", class_="title").text
            title = item.find("div", class_="desc").text
            if re.findall("\(After\)", artist):
                artist = re.sub("\(After\)", "", artist)
                title += " (After)"
            if re.findall(
                "[ㄱ-ㅣ가-힣]", item.find("div", class_="standard").find("span").text
            ):
                material_kor = item.find("div", class_="standard").find("span").text
            else:
                material_eng = item.find("div", class_="standard").find("span").text
            if item.find("div", class_="standard").find("div"):
                size_year = item.find("div", class_="standard").find("div").text
                for temp in size_year.split("|"):
                    if re.findall("\d\s*cm", temp):
                        size, desc_card = Size(temp)
                        height = size["height"]
                        width = size["width"]
                        depth = size["depth"]
                    else:
                        mfg_date = MfgDate(temp)

            for price in item.find("div", class_="price-box").find_all("dl"):
                if price.find("dt").text.lower() == "추정가":
                    estimate_min = re.sub("[^0-9]", "", price.find_all("dd")[0].text)
                    estimate_max = re.sub("[^0-9]", "", price.find_all("dd")[1].text)
                    if estimate_min:
                        currency = (price.find_all("dd")[0].text[:4]).upper().strip()
                if price.find("dt").text.lower() == "시작가":
                    start_bid = re.sub("[^0-9]", "", price.find("dd").text)
                    if start_bid and not currency:
                        currency = (price.find("dd").text[:4]).upper().strip()
                if price.find("dt").text.lower() == "낙찰가":
                    if price.find("dd").find("strong"):
                        winning_bid = re.sub(
                            "[^0-9]", "", price.find("dd").find("strong").text
                        )
                    if winning_bid:
                        if start_bid:
                            if float(start_bid) != 0:
                                competition = float(winning_bid) / float(start_bid) - 1
                            else:
                                competition = float(winning_bid) / 50000
                        elif estimate_min:
                            if start_bid != 0:
                                competition = (
                                    float(winning_bid) / float(estimate_min) - 1
                                )
                            else:
                                competition = float(winning_bid) / 50000
                        else:
                            competition = 0

                        if not currency:
                            currency = (price.find("dd").find("strong").text[:4]).upper().strip()
            # print(winning_bid)
            artist = Language(lang, artist)
            title = Language(lang, title)
            df["lot"].append(lot)
            df["img"].append(img)
            df["artist_" + lang].append(artist)
            df["title_" + lang].append(title)
            df["material_kor"].append(material_kor)
            df["material_eng"].append(material_eng)
            df["height"].append(height)
            df["width"].append(width)
            df["depth"].append(depth)
            df["mfg_date"].append(mfg_date)
            df["desc_card"].append(desc_card.lower())
            df["currency"].append(currency)
            df["estimate_min"].append(estimate_min)
            df["estimate_max"].append(estimate_max)
            df["start_price"].append(start_bid)
            df["hammer_price"].append(winning_bid)
            df["competition"].append(competition)
            detail_url.append("{0}/{1}".format(url, lot))
    return pd.DataFrame(df), detail_url


def Detail(driver, url, lang):
    print("데이터 수집중 (상세페이지)")
    df = {
        "lot": [],
        "img": [],
        "artist_" + lang: [],
        "artist_birth": [],
        "artist_death": [],
        "title_" + lang: [],
        "signed": [],
        "frame": [],
        "condition_report": [],
        "desc_detail": [],
        "literature": [],
        "exhibited": [],
        "provenance": [],
    }
    for detail_url in url:
        lot, img, artist, artist_birth, artist_death, title, frame = "", "", "", "", "", "", ""
        signed, desc, provenance, condition, exhibited, literature = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        driver.get(detail_url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        lot = soup.find("div", class_="index-box").find("span").text
        if soup.find("strong", {"id": "data-artist-name"}):
            artist = soup.find("strong", {"id": "data-artist-name"}).text
        if soup.find("strong", {"ng-bind": "displayLotInfo.artistName"}):
            artist = soup.find("strong", {"ng-bind": "displayLotInfo.artistName"}).text
        if soup.find("span", {"id": "data-artist-born-year"}):
            artist_date = re.sub(
                "[^0-9-~]", "", soup.find("span", {"id": "data-artist-born-year"}).text
            )
        if soup.find("span", {"ng-bind": "displayLotInfo.birthOfDeath"}):
            artist_date = re.sub(
                "[^0-9-~]",
                "",
                soup.find("span", {"ng-bind": "displayLotInfo.birthOfDeath"}).text,
            )
        artist_birth = ""
        artist_death = ""
        match_artist_date = re.findall(r"\d+", artist_date)
        if len(match_artist_date) == 1:
            artist_birth = match_artist_date[0]
        elif len(match_artist_date) == 2:
            artist_birth = match_artist_date[0]
            artist_death = match_artist_date[1]


        if soup.find("span", {"id": "data-lot-title"}):
            title = soup.find("span", {"id": "data-lot-title"}).text
        if soup.find("span", {"ng-bind": "displayLotInfo.lotTitle"}):
            title = soup.find("span", {"ng-bind": "displayLotInfo.lotTitle"}).text
        for i in (
            soup.find("div", class_="info-box")
            .find("div", class_="desc")
            .find_all("span")
        ):
            if re.findall(
                "inscribed|titled|dated|stamped|incised|signature|numbered",
                i.text.lower(),
            ) or re.match("(each\s*)?signed", i.text.lower()):
                signed.append(i.text.strip())
            desc.append(i.text.strip())
        for sub in soup.find_all("div", class_="info-sub-box"):
            if sub.find("div", class_="tit tt5"):
                if sub.find("div", class_="tit tt5").text == "CONDITION":
                    for i in sub.find("div", class_="desc").get("title").split("\n"):
                        if re.findall("framed", i.lower()):
                            frame = i
                            if re.match("unframed", frame.lower()):
                                frame = ""
                        elif i.strip():
                            condition.append(i)
                if sub.find("div", class_="tit tt5").text == "PROVENANCE":
                    provenance = sub.find("div", class_="desc").get("title").split("\n")
                if sub.find("div", class_="tit tt5").text == "EXHIBITED":
                    exhibited = sub.find("div", class_="desc").get("title").split("\n")
                if sub.find("div", class_="tit tt5").text == "LITERATURE":
                    literature = sub.find("div", class_="desc").get("title").split("\n")
        if re.findall("\(After\)", artist):
            artist = re.sub("\(After\)", "", artist)
            title += " (After)"
        artist = Language(lang, artist)
        title = Language(lang, title)
        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_" + lang].append(artist)
        df["title_" + lang].append(title)

        # df["artist_date"].append(artist_date)
        df["artist_birth"].append(artist_birth)
        df["artist_death"].append(artist_death)

        df["signed"].append(" / ".join(signed))
        df["frame"].append(frame)
        df["condition_report"].append(" / ".join(condition))
        df["desc_detail"].append(" / ".join(desc))
        df["provenance"].append(" / ".join(provenance))
        df["exhibited"].append(" / ".join(exhibited))
        df["literature"].append(" / ".join(literature))
    return pd.DataFrame(df)


def apply_sellingPrice(kind, winning_bid, transact_date):
    if not winning_bid:
        return ""
    date1 = datetime.strptime("{0}-{1}-{2}".format(2020, 8, 16), "%Y-%m-%d")
    if kind == "offline":
        return float(winning_bid) * 1.198
    else:
        if transact_date >= date1:
            return float(winning_bid) * 1.198
        else:
            return float(winning_bid) * 1.165


def main(driver, df):
    load_dotenv()
    print("서울옥션 접속 중...")

    driver.get("https://seoulauction.com/login")
    print("서울옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@id='loginId']").send_keys(
        os.environ.get("auctionID2")
    )
    driver.find_element_by_xpath("//*[@id='password']").send_keys(
        os.environ.get("auctionPW2")
    )
    driver.find_element_by_xpath("//*[@class='btn btn_point btn_lg']").click()
    driver.get("https://seoulauction.com/auction/progress")
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    count = 1
    temp = ""
    auction = []
    for i in soup.find_all("div", class_="typo-area"):
        if i.find("div", class_="state-box").text.lower().strip() != "online":
            kind = "offline"
        else:
            kind = "online"
        name = i.find("div", class_="title-box").text.strip()
        transact_y, transact_m, transact_d = "", "", ""
        for dl in i.find("div", class_="info-box").find_all("dl"):
            if dl.find("dt").text == "경매일":
                md = dl.find("dd").text.split("(")[0].split("/")
                if md[0].strip() == "1" and datetime.today().month != 1:
                    transact_y = datetime.today().year + 1
                else:
                    transact_y = datetime.today().year
                transact_m = int(md[0].strip())
                transact_d = int(md[1].strip())
                transact_date = datetime.strptime("{0}-{1}-{2}".format(transact_y,transact_m,transact_d), "%Y-%m-%d")
        auction.append(
            {
                "name": name,
                "kind": kind,
                "transact_date": transact_date,
                "transact_y": transact_y,
                "transact_m": transact_m,
                "transact_d": transact_d,
            }
        )
        temp += "{0} : ({1}) {2}\n".format(count, kind, name)
        count += 1
    while True:
        print("-" * 20)
        print(temp)
        print(count, ": url 직접입력")
        print("q : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        errmsg = "보기의 번호를 제대로 입력해주세요."
        if answer.isdigit():
            if count > int(answer) and answer != "0":
                driver.find_element_by_xpath(
                    "/html/body/div/div/div[1]/div/section[2]/div/div/div/ul/li[{0}]/div/article/div[2]/div/div[4]/button".format(
                        int(answer)
                    )
                ).click()
                break
            elif count == int(answer):
                url = input("url 입력 : ")
                onoff = input("[ 1:online / 2:offline ] 입력 : ")
                if onoff == "1":
                    kind = "online"
                elif onoff == "2":
                    kind = "offline"
                else:
                    print(errmsg)
                    driver.find_element_by_xpath("//*[@class='utility-login']").click()
                    return None, None
                driver.get(url)
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                name = soup.find("h2", class_="page_title").text.strip()
                for i in soup.find("ul", class_="event_day-list").find_all("li"):
                    if "경매일" in i.text:
                        transact_date = i.find_all("span")[1].text.split("(")[0]
                        break
                else:
                    print("경매날짜를 찾을 수 없습니다.")
                    transact_d = "00/00"
                # transact_date = (
                #     soup.find("ul", class_="event_day-list")
                #     .find("span", class_="to-date")
                #     .text.split("(")[0]
                # )
                transact_m = re.sub("[^0-9]", "", transact_date.split("/")[0])
                transact_d = re.sub("[^0-9]", "", transact_date.split("/")[1])
                if transact_m == "1" and datetime.today().month != 1:
                    transact_y = datetime.today().year + 1
                else:
                    transact_y = datetime.today().year
                transact_date = datetime.strptime("{0}.{1}.{2}".format(transact_y,transact_m,transact_d), "%Y.%m.%d")
                auction.append(
                    {
                        "name": name,
                        "kind": kind,
                        "transact_date" : transact_date,
                        "transact_y": transact_y,
                        "transact_m": transact_m,
                        "transact_d": transact_d,
                    }
                )
                break
            else:
                print(errmsg)

        elif answer == "q":
            driver.find_element_by_xpath("//*[@class='utility-login']").click()
            return None, None
        else:
            print(errmsg)

    df_card, detail_url = Card(driver, "kor")
    df = df.drop(["img"], axis=1)
    driver.get("https://seoulauction.com/?lang=en")
    if int(answer) == count:
        driver.get(url)
        df_card_eng, detail_url = Card(driver, "eng")
        df_card_eng = df_card_eng[["lot", "artist_eng", "title_eng"]]
        df = pd.merge(df_card, df_card_eng, how="outer", on="lot")
        df["description"] = df["desc_card"]
        df = df.drop(["desc_card"], axis=1)
    else:
        df_detail = Detail(driver, detail_url, "eng")
        df_detail = df_detail.drop(["img"], axis=1)
        df = pd.merge(df_card, df_detail, how="outer", on="lot")
        df["description"] = df.apply(lambda x: (x.desc_card if type(x.desc_card)== str else "") +(x.desc_detail if type(x.desc_detail)== str else "") , axis=1)
        df = df.drop(["desc_card", "desc_detail"], axis=1)
    df["material_kind"] = df.apply(
        lambda x: Material(x.material_kor, x.material_eng, x.description), axis=1
    )
    df["company"] = "서울옥션"
    df["auction_name"] = auction[int(answer) - 1]["name"]
    df["transact_date"] = auction[int(answer) - 1]["transact_date"]
    df["on_off"] = auction[int(answer) - 1]["kind"]
    df["selling_price"] = df.apply(
        lambda x: apply_sellingPrice(
            x.on_off, x.hammer_price, x.transact_date
        ),
        axis=1,
    )
    df["usd_estimate_min"] = ""
    df["usd_estimate_max"] = ""
    df["usd_start_price"] = ""
    df["usd_hammer_price"] = ""
    df["usd_selling_price"] = ""
    if re.findall("홍콩|hongkong|hong kong", auction[int(answer) - 1]["name"].lower()):
        df["location"] = "Hong Kong"
    else:
        df["location"] = "Korea"
    
    driver.find_element_by_xpath("//*[@class='utility-login']").click()
    driver.get("https://seoulauction.com/?lang=ko")
    return df, auction[int(answer) - 1]["kind"]