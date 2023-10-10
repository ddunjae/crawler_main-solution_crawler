from cmath import nan
from types import NoneType
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
from dotenv import load_dotenv
import os
from defines.dataframe import dataframe as create_df
import requests


# 카드페이지에서 영문데이터 수집
def data_aauction(_driver, url, _df):
    print(_df)
    url_list = []
    print("데이터 수집 중...")
    df = create_df(["lot", "img", "artist_kor", "artist_eng", "artist_birth", "artist_death", "title_kor", "title_eng", "material_kor", "material_eng", "material_kind",
               "height", "depth", "width", "mfg_date", "frame", "estimate_min", "estimate_max", "competition", "selling_price", "start_price", "hammer_price"], dict)
    auction_name = ""
    transactDate = ""

    for p in range(1, 100):
        _driver.get(url + "&page=" + str(p))
        html = _driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
        soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
        if not (soup.find("div", class_="alist").find_all("li")):  # 페이지 끝까지 다가면 break
            soup.find("section", class_="auction-headers").find(
                "div", class_="left"
            ).span.extract()
            info = (
                soup.find("section", class_="auction-headers")
                .find("div", class_="left")
                .text.split("\n")
            )
            auction_name = "에이옥션 " + info[2].strip()
            transactDate = datetime.strptime(
                re.findall(".+?[년].+?[월].+?[일]", info[3])[0].strip(), "%Y년 %m월 %d일"
            )
            break
        for i in soup.find("div", class_="alist").find_all("a"):
            if not i.find("div", class_="list-lot"):
                continue
            url_list.append(i.get("href"))

    for url in url_list:        
        _driver.get(url)
        html = _driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
        soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정
        (
            img,
            artist_kor,
            artist_eng,
            artist_date,
            artist_birth,
            artist_death,
            title_kor,
            title_eng,
            material_kor,
            material_eng,
            size,
            mfg_date,
            frame,
            estimate_min,
            estimate_max,
            start_bid,
            hammer_price,
            selling_price,
            competition,
        ) = (
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan,
            nan
        )
        lot = soup.find("li", class_="lot").find("span").text
        img = soup.find("img", id="art_mimgs").get("src")
        artist_kor = soup.find("li", class_="name-ko").text.strip()
        artist_eng = re.sub(
            "[^a-zA-Z -]", "", soup.find("li", class_="name-etc").text
        ).strip()
        artist_date = re.sub("~", "-", soup.find("li", class_="birth").text).strip().split('-')
        if len(artist_date) > 0:
            artist_birth = artist_date[0].strip()
            if len(artist_date) > 1:
                artist_death = artist_date[-1].strip()
        print(artist_birth, artist_death)
        title_kor = soup.find("li", class_="art-name-ko").text
        title_eng = soup.find("li", class_="art-name-en").text
        material_kor = re.sub(
            " " * 15, "", soup.find("li", class_="art-material").text
        ).strip()
        material_eng = re.sub(
            " " * 15, "", soup.find("li", class_="art-material2").text
        ).strip()
        if re.findall(
            "패브릭|캔버스|컨버스|린넨|리넨|아마|마포|마대|코튼|면|천|직물|canvas|linen|hemp|cloth|fabric",
            (material_kor + material_eng).lower(),
        ):
            material_kind = "캔버스"
        elif re.findall(
            "목판|판넬|패널|나무패널|나무보드|메소나이트|합판|보드|wooden board|wooden panel|panel|masonite|board",
            (material_kor + material_eng).lower(),
        ):
            if re.findall(
                "종이보드|종이 보드|하드보드|하드 보드|paper board|hardboard|cardboard",
                (material_kor + material_eng).lower(),
            ):
                material_kind = "종이"
            else:
                material_kind = "패널"
        elif re.findall(
            "판화|에칭|드라이포인트|인그레이빙|틴트|프린트|스크린|스텐실|세리그라프|리놀륨|리노컷|고무판화|포토그라비어|콜라그래프|print|woddcut|intaligo|etching|drypoing|ingraving|tint|screen|serigraph|stencil|lithograph|linoleum|linocut|offset|pigment|monotype|rubber print",
            (material_kor + material_eng).lower(),
        ):
            if re.findall(
                "chrom|gelatin|lambda|c-|크로모제닉|크롬|젤라틴|람다",
                (material_kor + material_eng).lower(),
            ):
                material_kind = "사진"
            else:
                material_kind = "판화"
        elif re.findall("사진|photograph", (material_kor + material_eng).lower()):
            material_kind = "사진"
        elif re.findall(
            "종이|원고지|편지|한지|화선지|닥지|닥종이|장지|순지|골판지|신문지|엽서|봉투|paper|manuscript|envelope|hanji|dak|news|postcard",
            (material_kor + material_eng).lower(),
        ):
            material_kind = "종이"
        elif re.findall(
            "레진|합성수지|알루미늄|브론즈|스틸|스테인리스|철|돌|나무|대리석|화강암|테라코타|resin|synthetic|pvc|aluminum|bronze|steel|stainless|iron|stone|wood|marble|granite|terracotta",
            (material_kor + material_eng).lower(),
        ):
            material_kind = "조각"
        elif re.findall(
            "토기|도기|석기|자기|도자기|세라믹|유리|clay|earthenware|stoneware|porcelain|glazed|ceramic|glass",
            (material_kor + material_eng).lower(),
        ):
            material_kind = "도자"
        else:
            material_kind = "기타"

        size = re.sub(" ", "", soup.find("li", class_="art-size").text).strip()
        size = size.split("×")
        height = re.sub("[^0-9.]", "", size[0])
        if len(size) >= 2:
            width = re.sub("[^0-9.]", "", size[1])
            if len(size) == 3:
                depth = re.sub("[^0-9.]", "", size[2])
            else:
                depth = nan
        else:
            width, depth = nan, nan
        for art_make in soup.find_all("li", class_="art-make"):
            if re.match("액자상태", art_make.text):
                frame = art_make.text[6:].strip()
            elif re.match("작품상태", art_make.text):
                continue
            else:
                mfg_date = re.sub("~", "-", art_make.text)
        price_info = str(soup.find("div", "rinfo-price"))
        estimate = (
            re.sub(
                "[^0-9~]",
                "",
                re.findall(
                    "(?:.+추정가</li><li>)(.+?</li>)", re.sub("\n", "", price_info)
                )[0],
            )
        ).split("~")
        estimate_min = estimate[0]
        estimate_max = estimate[1]
        start_bid = re.sub(
            "[^0-9]",
            "",
            re.findall("(?:.+시작가</li><li>)(.+?</li>)", re.sub("\n", "", price_info))[0],
        )
        if soup.find("div", {"id": "bid-num"}).text.strip() != "0":
            winning_bid = re.sub(
                "[^0-9]", "", soup.find("div", {"id": "nowprice"}).text
            )
        else:
            winning_bid = ""
        if winning_bid != "":
            selling_price = int(winning_bid) * 1.165
            if start_bid != "" and start_bid != "0":
                competition = (int(winning_bid) / int(start_bid)) - 1
        print(start_bid)
        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_kor"].append(artist_kor)
        df["artist_eng"].append(artist_eng)
        df["artist_birth"].append(artist_birth)
        df["artist_death"].append(artist_death)
        df["title_kor"].append(title_kor)
        df["title_eng"].append(title_eng)
        df["material_kor"].append(material_kor)
        df["material_eng"].append(material_eng)
        df["height"].append(height)
        df["width"].append(width)
        df["depth"].append(depth)
        df["mfg_date"].append(mfg_date)
        df["frame"].append(frame)
        df["estimate_min"].append(estimate_min)
        df["estimate_max"].append(estimate_max)
        df["start_price"].append(start_bid)
        df["hammer_price"].append(winning_bid)
        df["selling_price"].append(selling_price)
        df["material_kind"].append(material_kind)
        df["competition"].append(competition)

    temp = pd.DataFrame(df)
    _df = pd.concat([_df, temp], ignore_index=True)

    print(auction_name, transactDate)
    _df["auction_name"] = auction_name  # 경매명
    _df["transact_date"] = transactDate

    return _df


def main(driver, df):
    load_dotenv()
    print("에이옥션 접속 중...")
    driver.get("https://a-auction.co.kr/user/login.html?urd=https://a-auction.co.kr/")
    print("에이옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@id='login_id']").send_keys(
        os.environ.get("auctionID3")
    )
    driver.find_element_by_xpath("//*[@id='login_pw']").send_keys(
        os.environ.get("auctionPW4")
    )
    driver.find_element_by_xpath("//*[@type='submit']").click()

    while True:
        print("-" * 20)
        print("1 : online\n2 : 직접입력\nq : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer == "q":
            driver.get(
                "https://www.a-auction.co.kr/user/logout.html?urd=https://www.a-auction.co.kr/page/page.html?mcd=03/01&atcode=AC35971925&at_part="
            )
            return None, None
        elif answer == "1":
            html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
            soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정

            auction_list = []  # 진행중인 경매
            for auction in soup.find("ul", class_="tmenu").find_all("a"):
                if auction.find("div", class_="onbtn"):
                    if auction.find("div", class_="onbtn").text == "ON":
                        auction_list.append(auction.get("href"))
            if len(auction_list) == 0:
                print("진행중인 경매가 없습니다.")
                driver.get(
                    "https://www.a-auction.co.kr/user/logout.html?urd=https://www.a-auction.co.kr/"
                )
                return None, None
            break
        elif answer == "2":
            url = input("url을 입력하세요")
            auction_list = [url]
            break
        else:
            print("보기의 번호를 제대로 입력해주세요.")
            
    for url in auction_list:
        df = data_aauction(driver, url, df)

    df["company"] = "에이옥션"  # 출품처
    df["on_off"] = "online"  # 온라인/오프라인 구분
    df["currency"] = "KRW"
    df["location"] = "Korea"
    # 끝나면 브라우져 닫기
    print("데이터 수집을 완료했습니다.")
    # 로그아웃

    print(df)
    driver.get(
        "https://www.a-auction.co.kr/user/logout.html?urd=https://www.a-auction.co.kr/page/page.html?mcd=03/01&atcode=AC35971925&at_part="
    )
    return df, ""
