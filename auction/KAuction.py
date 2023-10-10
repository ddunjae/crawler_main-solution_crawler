from cmath import nan
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import os
import time
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate

# 카드페이지에서 데이터 수집
def Card(_driver, _url, _df, lang, onoff):
    url_list = []
    print("데이터 수집 중(1/2)")
    _driver.get(_url)
    soup = BeautifulSoup(_driver.page_source, "html.parser")
    for i in soup.find("div", class_="btn-group list-btn-wrap").find_all(
        "li", class_="nav-item"
    ):
        if "전체" == i.text.strip() or "All" == i.text.strip():
            continue
        if (
            "주얼리" in i.text
            or "명품" in i.text
            or "Jewels" in i.text
            or "Luxuries" in i.text
            or "Luxury" in i.text
        ):
            material_kind = "Watch&Jewelry&Handbags"
        else:
            material_kind = ""
        work_type = re.sub("section-", "?work_type=", i.find("a").get("id"))

        for p in range(1, 100):
            _driver.get(_url + work_type + "&page=" + str(p))
            time.sleep(1)
            html = _driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
            soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
            if soup.find("div", class_="ico-page text-center"):  # 페이지 끝까지 다가면 break
                break
            for i in soup.find_all("div", class_="col mb-4 list-pd"): #메이저 경매일시 major-list-pd 추가
                description = []
                if not (i.find("a")):
                    continue
                url_list.append((i.find("a")).get("href"))
                # LOT
                lot = (i.find("div", class_="lot").text[4:]).strip()
                # 작품명
                title = i.find("h5", class_="card-subtitle text-truncate").text
                # 작가명
                artist = (i.find("h5", class_="card-title text-truncate").text).strip()
                if re.findall("\(아트상품\)|\(사후판화\)", artist):
                    for temp in re.findall("\(아트상품\)|\(사후판화\)", artist):
                        title += " " + temp
                    artist = re.sub("\(아트상품\)|\(사후판화\)", "", artist)
                if re.match("After", artist):
                    title += " (After)"
                artist = Language(lang, artist)
     
                title = Language(lang, title)
                # 재료 및 기법
                material = (
                    i.find("p", class_="description text-truncate")
                    .find("span")
                    .get("title")
                )
                material = Language(lang, material)
                # 사이즈, 제작연도, desc
                if lang == "kor":
                    size, mfg_date = "", ""
                    if i.find("span", class_="text-truncate").text.strip():
                        size = i.find("span", class_="text-truncate").text.split(" | ")[0]
                        if " | " in i.find("span", class_="text-truncate").text:
                            mfg_date = MfgDate(i.find("span", class_="text-truncate").text.split(" | ")[1])
                    size, etc = Size(size)
                    description.append(etc)
                    description = " / ".join(description)
                    temp = pd.DataFrame(
                        {
                            "lot": [lot],
                            "artist_" + lang: [artist],
                            "title_" + lang: [title],
                            "description": [description],
                            "mfg_date": [mfg_date],
                            "height": [size["height"]],
                            "width": [size["width"]],
                            "depth": [size["depth"]],
                            "material_" + lang: [material],
                            "material_kind": [material_kind],
                        }
                    )
                    _df = pd.concat([_df, temp], ignore_index=True)
                else:  # 이미지, 가격정보fas fa-list-ul
                    (
                        img,
                        currency,
                        estimate_min,
                        estimate_max,
                        start_bid,
                        winning_bid,
                        selling_price,
                        competition,
                    ) = ("", "", "", "", "", "", "", "")
                    if i.find("img"):
                        img = re.sub(
                            "1001.jpg", "4001.jpg", i.find("img").get("data-src")
                        )
                    for price in i.find("div", class_="card-text dotted").find_all(
                        "ul", class_="list-inline"
                    ):
                        if "Estimate" in price.text:
                            currency = price.find_all("li")[1].text.strip()[:3]
                            estimate_min = re.sub(
                                "[^0-9]", "", price.find_all("li")[1].text.split("~")[0]
                            )
                            if len(price.find_all("li")[1].text.split("~")) >= 2:
                                estimate_max = re.sub(
                                    "[^0-9]",
                                    "",
                                    price.find_all("li")[1].text.split("~")[1],
                                )
                        if "Starting" in price.text:
                            if not currency:
                                currency = price.find_all("li")[1].text.strip()[:3]
                            start_bid = re.sub(
                                "[^0-9]", "", price.find_all("li")[1].text
                            )
                        if "Hammer" in price.text:
                            if not currency:
                                currency = price.find_all("li")[1].text.strip()[:3]
                            winning_bid = re.sub(
                                "[^0-9]", "", price.find_all("li")[1].text
                            )
                            if onoff == "online":
                                if int(winning_bid) <= 10000000:
                                    selling_price = int(winning_bid) * 1.165
                                else:
                                    selling_price = (
                                        10000000 * 1.165
                                        + (int(winning_bid) - 10000000) * 1.198
                                    )
                            else:
                                selling_price = 10000000 * 1.165 + (int(winning_bid) - 10000000) * 1.198
                                
                                
                            if start_bid:
                                competition = float(winning_bid) / float(start_bid) - 1
                            elif estimate_min:
                                competition = (
                                    float(winning_bid) / float(estimate_min) - 1
                                )
                            else:
                                competition = 0
                    temp = pd.DataFrame(
                        {
                            "lot": [lot],
                            "img": [img],
                            "artist_" + lang: [artist],
                            "title_" + lang: [title],
                            "material_" + lang: [material],
                            "currency": [currency],
                            "estimate_min": [estimate_min],
                            "estimate_max": [estimate_max],
                            "start_price": [start_bid],
                            "hammer_price": [winning_bid],
                            "selling_price": [selling_price],
                            "competition": [competition],
                        }
                    )
                    _df = pd.concat([_df, temp], ignore_index=True)
    if lang == "kor":
        company = (soup.find("div", class_="subtop-desc")).find("h1").text  # 경매명
        _df["auction_name"] = company
        transact_date = datetime.strptime(
            re.findall(".+?[년].+?[월].+?[일]", company)[0].strip(), "%Y년 %m월 %d일"
        )  # 거래일
        _df["transact_date"] = transact_date
    return url_list, _df




# 상세페이지에서 영문데이터 수집
def Detail_eng(_driver, url_list, _df, onoff):
    # 영문 페이지로 바꿈
    _driver.get("https://www.k-auction.com/Home/SetLanguage?culture=ENG")
    print("데이터 수집 중(2/2)")
    print("↑ 시간이 걸릴 수 있습니다. 잠시 기다려주세요.")
    for page in url_list:
        _driver.get("https://www.k-auction.com" + page)
        time.sleep(2)
        html = _driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        artist = soup.select_one('p.writer > span:first-child').text.strip()  # 작가명(영문)
        artist = artist.split('\n')[0]
        
        artist_birth = ""
        artist_death = ""
        match_artist_date = re.findall(r"\d+", soup.select_one('p.writer > span:last-child').text.strip())
        if len(match_artist_date) == 1:
            artist_birth = match_artist_date[0]
        elif len(match_artist_date) == 2:
            artist_birth = match_artist_date[0]
            artist_death = match_artist_date[1]

        lot = (soup.find("div", class_="lot-num").text.strip()[4:]).strip()
        if soup.find("div", class_="slide"):
            img = soup.find("div", class_="slide").find("img").get("src")  # 이미지
        else:
            img = ""
        if soup.find("p", class_="writer").span:  # 생몰년
            writerD = re.sub(
                "[^0-9-]", " ", soup.find("p", class_="writer").span.extract().text
            ).strip()
        else:
            writerD = ""
      
        if re.search("[ㄱ-ㅣ가-힣]", artist):
            artist = ""
        # 작품명(영문)
        title = soup.find("p", class_="sub-tit").text
        if re.match("After", artist):
            artist = artist[len("After") :].strip()
            if "After" in title:
                title += "(After)"
        if re.search("[ㄱ-ㅣ가-힣]", title):
            title = ""
        if soup.find("div", class_="material").find("p"):
            material = re.sub(
                "\n", " ", soup.find("div", class_="material").find("p").text.strip()
            )  # 재료 및 기법(영문)
            if "cm|츠|㎝|mm|㎜" in material.lower():
                material = ""
            temp = _df[["material_kor", "material_kind", "description"]][_df.lot == lot]
            if "Watch&Jewelry&Handbags" not in temp.material_kor.iloc[0]:
                mk = Material(
                    material, temp.material_kor.iloc[0], temp.description.iloc[0]
                )
                _df.loc[_df["lot"] == lot, "material_kind"] = mk
        else:
            material = ""
        if soup.find("div", class_="cont"):
            signed, frame, provenance = [], [], ""
            temp = re.findall(
                "(?:.+PROVENANCE:)(.+?<br/><br/>)",
                str(soup.find("div", class_="cont").find("p")),
            )
            if temp:
                provenance = ("\n".join(s for s in (temp[0]).split("<br/>"))).strip()
            work_info = re.sub(
                "<p>", "", str(soup.find("div", class_="cont").find("p"))
            ).split("<br/>")

            for s in work_info:
                if "signed" in s:  # 사인위치
                    signed.append(s)
                if ("Frame" in s) or ("Screen" in s):  # 프레임
                    frame.append(s)
            signed, frame = "\n".join(s for s in signed), "\n".join(c for c in frame)
        condition_report = []
        if soup.find("div", class_="report"):
            if soup.find("div", class_="report").find("div", class_="cont"):
                for i in (
                    soup.find("div", class_="report")
                    .find("div", class_="cont")
                    .find_all("li")
                ):
                    if re.findall("[ㄱ-ㅣ가-힣]", i.text):
                        condition_report.append(i.text.strip())
        condition_report = " / ".join(condition_report)

        price = str(soup.find("div", class_="es-price"))
        if re.findall("(?:.+Estimate)(.+?</p>)", re.sub("\n", "", price)):
            estimate = re.sub(
                "[^0-9~]",
                "",
                re.findall("(?:.+Estimate)(.+?</p>)", re.sub("\n", "", price))[0],
            ).split("~")
            if estimate[0] != "":
                estimateMin = estimate[0]
                if len(estimate) >= 2:
                    estimateMax = estimate[1]                
                else: estimateMax = estimate[0]
            else:
                estimateMin, estimateMax = "", ""
        else:
            estimateMin, estimateMax = "", ""
        if re.findall("(?:.+Starting Bid)(.+?</p>)", re.sub("\n", "", price)):
            startPrice = re.sub(
                "[^0-9~]",
                "",
                re.findall("(?:.+Starting Bid<)(.+?<)", re.sub("\n", "", price))[0],
            )
        else:
            if estimateMin != "":
                startPrice = estimateMin
            else:
                startPrice = ""
        competition = ""
        selling_price = ""
        if soup.find("label", class_="price-max"):
            currentPrice = re.sub(
                "[^0-9~]", "", soup.find("label", class_="price-max").text
            )
            if startPrice != "":
                competition = (int(currentPrice) / int(startPrice)) - 1
        elif re.findall("(?:.+낙찰가)(.+?</p>)", re.sub("\n", "", price)):
            currentPrice = re.sub(
                "[^0-9~]",
                "",
                re.findall("(?:.+낙찰가<)(.+?<)", re.sub("\n", "", price))[0],
            )
            if startPrice != "":
                competition = (int(currentPrice) / int(startPrice)) - 1
        else:
            currentPrice = nan
        
        #selling_price 수식 
        if type(currentPrice) == str:
            if onoff == "online":
                if int(currentPrice) <= 10000000:
                    selling_price = int(currentPrice) * 1.165
                else:
                    selling_price = (
                        10000000 * 1.165 + (int(currentPrice) - 10000000) * 1.198
                    )
            else:
                selling_price = int(currentPrice) * 1.198
        
        

        _df.loc[(_df.lot == lot),
            [
                "img",
                "artist_eng",
                # "artist_data",
                "title_eng",
                "material_eng",
                "signed",
                "frame",
                "start_price",
                "hammer_price",
                "selling_price",
                "estimate_min",
                "estimate_max",
                "provenance",
                "competition",
                "condition_report",

                "artist_birth",
                "artist_death"
            ],
        ] = [
            img,
            artist,
            # writerD,
            title,
            material,
            signed,
            frame,
            startPrice,
            currentPrice,
            selling_price,
            estimateMin,
            estimateMax,
            provenance,
            competition,
            condition_report,

            artist_birth,
            artist_death
        ]
    return _df


# driver = webdriver.Chrome(path) #테스트용
def main(driver, df):
    load_dotenv()
    print("\n케이옥션 접속 중...")
    driver.get("https://www.k-auction.com/Home/SetLanguage?culture=KOR")
    html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
    soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
    print("\n케이옥션 로그인 중...")
    driver.execute_script("javascript:$.commonUtils.openLogin();")
    time.sleep(1)
    driver.find_element_by_xpath("//*[@id='modal-login-id']").send_keys(
        os.environ.get("auctionID1")
    )
    driver.find_element_by_xpath("//*[@id='modal-login-pwd']").send_keys(
        os.environ.get("auctionPW1")
    )
    driver.find_element_by_xpath(
        "//*[@class='btn btn-block btn-primary btn-lg m-t-10 m-b-10']"
    ).click()

    while True:
        print("-" * 20)
        print(
            "1 : Major\t(offline)\n2 : Premium\t(online)\n3 : Weekly\t(online)\n4 : 과거옥션\nq : 뒤로가기"
        )
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer == "1":
            if soup.find("li", class_="on Major-on"):
                if soup.find("li", class_="on Major-on").find("i", class_="menu_icon-circle"):
                    url = ((soup.find("li", class_="on Major-on")).find("a")).get("href")
                    kinds = ["major", "offline"]
                    break
                else:
                    print("진행중인 경매가 없습니다")
            else:
                print("진행중인 경매가 없습니다")
        elif answer == "2":
            if soup.find("li", class_="on Premium-on"):
                if soup.find("li", class_="on Premium-on").find("i", class_="menu_icon-circle"):
                    url = ((soup.find("li", class_="on Premium-on")).find("a")).get("href")
                    kinds = ["premium", "online"]
                    break
                else:
                    print("진행중인 경매가 없습니다")
            else:
                print("진행중인 경매가 없습니다")
        elif answer == "3":
            if soup.find("li", class_="on Weekly-on"):
                if soup.find("li", class_="on Weekly-on").find("i", class_="menu_icon-circle"):
                    url = ((soup.find("li", class_="on Weekly-on")).find("a")).get("href")
                    kinds = ["weekly", "online"]
                    break
                else:
                    print("진행중인 경매가 없습니다")
            else:
                print("진행중인 경매가 없습니다")
        elif answer == "4":

            def temp_material_fn(material_kind, material_kor, material_eng, desc):
                if not material_kind:
                    material_kind = Material(material_eng, material_kor, desc)
                return material_kind

            url = input("url을 입력하세요 : ")
            while True:
                kind = input("online:1 / offline:2   입력하세요 : ")
                if kind == "1":
                    kinds = ["past_online", "online"]
                    break
                if kind == "2":
                    kinds = ["past_offline", "offline"]
                    break
                if kind == "q":
                    return None, None
            _, df_kor = Card(driver, url, df, "kor", kinds[1])
            df_kor = df_kor[
                [
                    "lot",
                    "artist_kor",
                    "title_kor",
                    "description",
                    "mfg_date",
                    "height",
                    "width",
                    "depth",
                    "material_kor",
                    "material_kind",
                    "auction_name",
                    "transact_date",
                ]
            ]
            driver.get("https://www.k-auction.com/Home/SetLanguage?culture=ENG")
            _, df_eng = Card(driver, url, df, "eng", kinds[1])
            df_eng = df_eng[
                [
                    "lot",
                    "artist_eng",
                    "title_eng",
                    "material_eng",
                    "img",
                    "currency",
                    "estimate_min",
                    "estimate_max",
                    "start_price",
                    "hammer_price",
                    "selling_price",
                    "competition",
                ]
            ]
            df = pd.merge(df_kor, df_eng, how="outer", on="lot")

            df["material_kind"] = df.apply(
                lambda x: temp_material_fn(
                    x.material_kind, x.material_kor, x.material_eng, x.description
                ),
                axis=1,
            )
            df["company"] = "케이옥션"
            df["on_off"] = kinds[1]
            return df, kinds[0]
        elif answer == "q":
            driver.get("https://www.k-auction.com/Member/Logout?redirect=/")
            return None, None
        else:
            print("보기의 번호를 제대로 입력해주세요.")

    # try:
    #     url_list, df = KAuction_kor(driver, url, df)
    #     if url_list is None:
    #         driver.get("https://www.k-auction.com/Member/Logout?redirect=/")
    #         return None,None
    #     KAuction_eng(driver, url_list, df)
    # except Exception as e:
    #     print("크롤링에 실패하였습니다. 사이트 확인 필요\n",str(e))
    #     return None, None

    url_list, df = Card(driver, "https://www.k-auction.com" + url, df, "kor", kinds[1])
    df = Detail_eng(driver, url_list, df, kinds[1])

    df["company"] = "케이옥션"
    df["on_off"] = kinds[1]
    if re.findall("홍콩|hongkong|hong kong", (df["auction_name"].unique()[0]).lower()):
        df["location"] = "Hong Kong"
    else:
        df["location"] = "Korea"

    # 끝나면 브라우져 닫기
    print("데이터 수집을 완료했습니다.")
    print("케이옥션 로그아웃")
    driver.get("https://www.k-auction.com/Member/Logout?redirect=/")
    return df, kinds[0]
# https://www.k-auction.com/Auction/Major/157
