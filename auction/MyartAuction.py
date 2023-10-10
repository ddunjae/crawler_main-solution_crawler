############## 수정 필요 ##################
from cmath import nan
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from cleansing.Size import Size
from cleansing.Language import Language
from cleansing.Material import Material
from cleansing.MfgDate import MfgDate
from defines.dataframe import dataframe as create_df


def Card(driver, lang):
    print("데이터 수집 중 ...")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    categories = []
    df = create_df(
        [
            "lot",
            "artist_" + lang,
            # "artist_date",
            "artist_birth",
            "artist_death",
            "title_" + lang,
            "mfg_date",
            "material_" + lang,
            "material_kind",
            "estimate_min",
            "estimate_max",
            "start_price",
            "hammer_price",
            "currency",
            "height",
            "width",
            "depth",
            "description",
        ],
        dict,
    )
    for i in soup.find("ul", class_="cate").find_all("li"):
        if re.findall("전체|total", i.text.lower()):
            continue
        if re.findall("도자|공예", i.text.lower()):
            material_kind = "Sculpture"
        elif re.findall("가구", i.text.lower()):
            material_kind = "Furniture&Design"
        else:
            material_kind = ""

        categories.append(
            {"material_kind": material_kind, "url": i.find("a").get("href")}
        )
    url_list = []
    for category in categories:
        for page in range(1, 100):
            driver.get("{0}&page={1}".format(category["url"], page))
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            while soup.find("center"):
                driver.get("{0}&page={1}".format(category["url"], page))
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                

            if not soup.find_all("li", class_="item g_item"):
                if not soup.find("ul", class_= "auction_list type02"):
                    break
                else:
                    if not soup.find("ul", class_= "auction_list type02").find_all("li"):
                        break
                    else:
                        work_list = soup.find("ul", class_= "auction_list type02").find_all("li")
            else:
                work_list = soup.find_all("li", class_="item g_item")

            for lots in work_list:
                url_detail = lots.find("a", class_="bt_view_detail")
                if url_detail:
                    url_list.append(url_detail.get("href"))
                lot = lots.find("div", class_="num").text.strip()
                artist_date_temp = lots.find("div", class_="tit").find("span").text.strip()
                artist_date   = "-".join(re.findall("\d\d\d\d", artist_date_temp))
                if not '-' in artist_date :
                    artist_birth  = artist_date 
                    artist_death = ''
                else:
                    [artist_birth, artist_death] = artist_date.split('-')
                lots.find("div", class_="tit").span.extract()
                artist = lots.find("div", class_="tit").text.strip()
                lots.find("div", class_="m_info").div.extract()
                title = re.sub(
                    "\n", " ", lots.find("div", class_="m_info").text.strip()
                )
                if re.match(artist, title):
                    title = title[len(artist):].strip()
                material, mfg_date, height, width, depth = "", "", "", "", ""
                desc = []
                for d_info in re.split("\n|ㅣ", lots.find("div", class_="d_info").text):
                    if not mfg_date:
                        mfg_date = MfgDate(d_info)
                        if mfg_date:
                            continue
                    if not material:
                        if Material(d_info, "", ""):
                            material = d_info.strip()
                    if not (height or width or depth):
                        size, _etc = Size(d_info)
                        if _etc:
                            desc.append(d_info.strip())
                        height = size["height"]
                        width = size["width"]
                        depth = size["depth"]
                estimate_min, estimate_max, currency, winning_bid, start_bid = (
                    "",
                    "",
                    "",
                    "",
                    "",
                )
                for p_info in lots.find("div", class_="p_info").find_all("dl"):
                    if not currency:
                        currency = p_info.find(
                            "div", class_="g_list_currency"
                        ).text.strip()
                    if re.findall("추정가|Estimate", str(p_info.find("dt"))):
                        currency = p_info.find(
                            "div", class_="g_list_currency"
                        ).text.strip()
                        estimate_min = re.sub(
                            "[^0-9]",
                            "",
                            p_info.find(
                                "div", class_="{0}_min".format(currency.lower())
                            ).text,
                        )
                        estimate_max = re.sub(
                            "[^0-9]",
                            "",
                            p_info.find(
                                "div", class_="{0}_max".format(currency.lower())
                            ).text,
                        )

                    if re.findall("시작가|Start", str(p_info.find("dt"))):
                        start_bid = re.sub(
                            "[^0-9]",
                            "",
                            p_info.find(
                                "div", class_="g_list_big_size_money_font"
                            ).text,
                        )
                    if re.findall("현재가|Current", str(p_info.find("dt"))):
                        winning_bid = re.sub(
                            "[^0-9]",
                            "",
                            p_info.find(
                                "div",
                                class_="g_current_price g_list_big_size_money_font",
                            ).text,
                        )
                    # override winning_bid
                    if re.findall("낙찰가", str(p_info.find("dt"))):
                        winning_bid = re.sub(
                            "[^0-9]",
                            "",
                            p_info.find(
                                "div",
                                class_="g_list_min_max_money",
                            ).text,
                        )

                artist = Language(lang, artist)
                title = Language(lang, title)
                material = Language(lang,material)
                df["lot"].append(lot)
                df["artist_" + lang].append(artist)
                #df["artist_date"].append(artist_date)
                df["artist_birth"].append(artist_birth)
                df["artist_death"].append(artist_death)
                df["title_" + lang].append(title)
                df["mfg_date"].append(mfg_date)
                df["material_" + lang].append(material)
                df["material_kind"].append(material_kind)
                df["estimate_min"].append(estimate_min)
                df["estimate_max"].append(estimate_max)
                df["start_price"].append(start_bid)
                df["hammer_price"].append(winning_bid)
                df["currency"].append(currency)
                df["height"].append(height)
                df["width"].append(width)
                df["depth"].append(depth)
                df["description"].append(" / ".join(desc))
                df['selling_price']=''
    return pd.DataFrame(df), url_list


def Detail(driver, url_list, lang):
    driver.find_element_by_xpath("/html/body/div[1]/div[1]/ul/li[3]/a[2]").click()
    df = create_df(
        [
            "lot",
            "img",
            "artist_" + lang,
            "title_" + lang,
            "material_" + lang
        ],
        dict,
    )
    for url in url_list:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        while soup.find("center"):
            driver.get(url)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        lot = soup.find("div", class_="num").text.strip()
        img  =""
        if soup.find("div", {"id":"img-1"}):
            temp=soup.find("div", {"id":"img-1"}).get("style")
            if re.findall("url\(\.(\/.*\.jpg)",temp):
                img = "https://myartauction.com"+re.findall("url\(\.(\/.*\.jpg)",temp)[0]
        artist = soup.find("div", class_="tit").text.strip()
        soup.find("div", class_="m_info").div.extract()
        title = soup.find("div", class_="tit").text
        material = []
        if soup.find("div", class_="d_info"):
            for txt in soup.find("div", class_="d_info").text.split("\n"):
                if txt.strip() == "":
                    continue
                if re.findall("cm|㎝",txt):
                    continue
                else:
                    material.append(txt.strip())
        artist = Language(lang, artist)
        title = Language(lang, title)
        material = Language(lang, "/".join(material))
                    
        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_" + lang].append(artist)
        df["title_" + lang].append(title)
        df["material_" + lang].append(material)
        print(img)
    driver.find_element_by_xpath("/html/body/div[1]/div[1]/ul/li[3]/a[2]").click()
    return pd.DataFrame(df)
    

def login(driver):
    # 로그인
    load_dotenv()
    driver.get("https://myartauction.com/index.php?mid=main&act=dispMemberLoginForm")
    print("\n마이아트옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@name='user_id']").send_keys(
        os.environ.get("auctionID2")
    )
    driver.find_element_by_xpath("//*[@name='password']").send_keys(
        os.environ.get("auctionPW2")
    )
    time.sleep(1)
    driver.find_element_by_xpath("//*[@class='bt_login']").click()


def logout(driver):
    print("마이아트옥션 로그아웃")
    driver.get("https://myartauction.com/index.php?mid=main&act=dispMemberLogout")


def main(driver, df):
    
    print("\n마이아트옥션 접속 중...")
    time.sleep(2)
    login(driver)

    html = driver.page_source  # 크롬브라우져에서 현재 불러온 소스 가져옴
    soup = BeautifulSoup(html, "html.parser")  # html 코드를 검색할 수 있도록 설정

    # 옥션종류 선택
    while True:
        print("-" * 20)
        print("1 : offline\n2 : online\n3: 종료 된 offline\nq : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        category = soup.findAll("ul", class_="depth2")
 
        if answer == "1":
            if category[0].find("a", class_="offline").find("i"):
                if category[0].find("a", class_="offline").find("i").text == "on":
                    driver.find_element_by_xpath("//*[@class='offline']").click()
                    kind = "offline"
                    url = driver.current_url
                break
            else:
                print("진행중인 경매가 없습니다.")
        elif answer == "2":
            if category[1].find("a", class_="online").find("i"):
                if category[1].find("a", class_="online").find("i").text == "on":
                    driver.find_element_by_xpath("//*[@class='online']").click()
                    kind = "online"
                    url = driver.current_url
                break
            else:
                print("진행중인 경매가 없습니다.")
        elif answer == "3":
            url = input("url 입력: ")
            driver.get(url)
            kind = ["offline", "오프라인"]
            break

        elif answer == "q":
            logout(driver)
            return None, None
        else:
            print("보기의 번호를 제대로 입력해주세요.")

    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    while soup.find("center"):
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    auction_name = soup.find("h2", class_="ai g_list_action_title").text.strip()
    for info in soup.find("div", class_="g_info").find_all("dl"):
        if kind == "online":
            if "종료일" in info.find("dt").text:
                transact_date = info.find("dd").text.split()[0]
                break
            else:
                continue
        else:
            if "일시" in info.find("dt").text:
                transact_date = info.find("dd").text.split()[0]
                break
            else:
                continue
    transact_date = datetime.strptime("-".join(transact_date.split("-")[:3]), "%Y-%m-%d")
    df_card, url_list = Card(driver, "kor")
    print("url_list", url_list)
    df_detail = Detail(driver, url_list, "eng")
    df = pd.merge(df_card, df_detail, how="outer", on="lot")

    df["company"] = "마이아트옥션"
    kind_adjusted = [kind] * len(df)
    df["on_off"] = kind_adjusted
    df["auction_name"] = auction_name
    if re.findall("홍콩|hongkong|hong kong", (df["auction_name"].unique()[0]).lower()):
        df["location"] = "Hong Kong"
    else:
        df["location"] = "Korea"
        df["transact_date"] = transact_date

    # 끝나면 브라우져 닫기
    print("데이터 수집을 완료했습니다.")
    logout(driver)
    return df, kind