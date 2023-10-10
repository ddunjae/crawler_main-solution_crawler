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
from urllib.parse import urlparse, parse_qs


def login(driver):
    load_dotenv()
    print("아이옥션 접속 중...")
    driver.get("https://www.insaauction.com/member/login.html")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    print("아이옥션 로그인 중...")
    driver.find_element_by_xpath("//*[@id='id']").send_keys(
        os.environ.get("auctionID2")
    )
    driver.find_element_by_xpath("//*[@id='pw']").send_keys(
        os.environ.get("auctionPW3")
    )
    driver.execute_script("javascript:fnc_login();")


def logout(driver):
    driver.get("https://www.insaauction.com/member/logout.php")

def Card(driver, url):
    url_list = []
    for page in range(0, 1000, 100):
        driver.get(url + "&list=" + str(page))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if soup.find("div", class_="checkerBoard"):
            div1_class = "checkerBoard"
            div2_class = "inbox"
            if not soup.find("div", class_="checkerBoard").find("li"):
                break
            for i in soup.find("div", class_="checkerBoard").find_all("div", class_="inbox"):
                if not i:
                    continue
                if i.find("a"):
                    url_list.append("https://www.insaauction.com" + i.find("a").get("href"))
        elif soup.find("div", class_="auctionList"):
            div1_class = "auctionList"
            div2_class = "list"
        else:
            break

        if not soup.find("div", class_=div1_class).find("li"):
            break
        for i in soup.find("div", class_=div1_class).find_all("div", class_=div2_class):
            if not i:
                continue
            if i.find("a"):
                url_list.append("https://www.insaauction.com" + i.find("a").get("href"))
    return url_list


def Detail(driver, url_list):
    df = create_df(["lot", "img", "artist_kor", "artist_eng","title_kor","title_eng","material_kind","material_kor","material_eng",
                    "height", "width", "depth", "mfg_date","signed", "certification", "frame", "estimate_min", "estimate_max", "start_price",
                    "hammer_price", "selling_price", "competition", "description"], dict)
    

    for url in url_list:
        etc = ""
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        img = "https://www.insaauction.com" + soup.find(
            "div", class_="swiper-slide"
        ).find("img").get("src")
        lot = str(int(soup.find("div", class_="lot").text.strip()))
        cnt = 0
        for i in soup.find("div", {"id": "rsection"}).find_all(
            "div", class_="name"
        ):
            cnt_k = 0
            if cnt == 0:
                artist_date = re.sub(
                    "~", " - ", re.sub("[^0-9~]", "", i.span.extract().text)
                ).strip()
                if artist_date:
                    if artist_date[-1] == "-":
                        artist_date = artist_date[:-2]
                for k in i.find_all("p"):
                    if cnt_k == 0:
                        artist_kor = re.sub("작자미상", "", k.text.strip())
                    elif cnt_k == 2:
                        artist_eng = re.sub("Unknown", "", k.text.strip())
                    cnt_k += 1
            elif cnt == 1:
                for k in i.find_all("p"):
                    if cnt_k == 0:
                        title_kor = k.text
                    elif cnt_k == 2:
                        title_eng = k.text
                    cnt_k += 1
            cnt += 1
        cnt = 0
        material_kor, material_eng = "", ""
        for i in soup.find("div", class_="imgInfo").find_all("p"):
            if cnt == 0:
                material = re.sub("/n", "", str(i)).split("<br/>")
                material_kor = re.sub("<p>", "", material[0]).strip()
                material_eng = re.sub("</p>", "", material[1]).strip()
            elif cnt == 1:
                size_ = i.text
                size, etc = Size(size_)
                height = size["height"]
                width = size["width"]
                depth = size["depth"]
            elif cnt == 2:
                mfg_date = MfgDate(re.sub("[()]", "", i.text))
            elif cnt == 3:
                signed = i.text
            elif cnt == 5:
                if "보존" in i.text:
                    frame = nan
                else:
                    frame = i.text
            elif cnt == 6:
                if "보증서" in i.text:
                    certification = i.text
                else:
                    certification = nan
            cnt += 1
        if soup.find("div", class_="amount").find("li"):
            estimate = re.sub(
                "[^0-9~]", "", soup.find("div", class_="amount").find("li").text
            ).split("~")
        else:
            estimate = re.sub(
                "[^0-9~]", "", soup.find("div", class_="amount").text
            ).split("~")

        if estimate:
            estimate_min, estimate_max = estimate[0], estimate[1]
        else:
            estimate_min, estimate_max = nan, nan
        if soup.find("div", class_="startPrice"):
            start_bid = re.sub(
                "[^[0-9]", "", soup.find("div", class_="startPrice").text
            )
        else:
            start_bid = ""
        if soup.find("div", class_="currentBid"):
            winning_bid = re.sub(
                "[^[0-9]",
                "",
                soup.find("div", class_="currentBid")
                .find("p", {"id": "bidding_max"})
                .text,
            )
            if winning_bid == "" or winning_bid == "0":
                winning_bid, competition, selling_price = nan, nan, nan
            else:
                if start_bid != "":
                    competition = (int(winning_bid) / int(start_bid)) - 1
                elif estimate_min != "" and type(estimate_min) == str:
                    competition = (int(winning_bid) / int(estimate_min)) - 1
                selling_price = float(winning_bid) * 1.165
        else:
            winning_bid, competition, selling_price = "", "", ""

        material_kind = Material(material_eng, material_kor, etc)
        df["description"].append(etc)
        df["lot"].append(lot)
        df["img"].append(img)
        df["artist_kor"].append(artist_kor)
        df["artist_eng"].append(artist_eng)
        #df["artist_date"].append(artist_date)
        df["title_kor"].append(title_kor)
        df["title_eng"].append(title_eng)
        df["material_kor"].append(material_kor)
        df["material_eng"].append(material_eng)
        df["material_kind"].append(material_kind)
        df["height"].append(height)
        df["width"].append(width)
        df["depth"].append(depth)
        df["mfg_date"].append(mfg_date)
        df["frame"].append(frame)
        df["estimate_min"].append(estimate_min)
        df["estimate_max"].append(estimate_max)
        df["start_price"].append(start_bid)
        df["hammer_price"].append(winning_bid)
        df["signed"].append(signed)
        df["certification"].append(certification)
        df["competition"].append(competition)
        df["selling_price"].append(selling_price)
    return pd.DataFrame(df)
    
def handle_crawl_past_with_url(soup: BeautifulSoup, driver):
    df = create_df(["lot", "img", "artist_kor", "artist_eng", "title_kor","title_eng","material_kind","material_kor","material_eng", "height", "width", "depth", "mfg_date","signed", "certification", "frame", "estimate_min", "estimate_max", "start_price", "hammer_price", "selling_price", "competition", "description", "transact_date", "company", "currency", "location", "auction_name", "artist_birth", "artist_death"], dict)

    auction_name = soup.find("div", class_="proceed").find("p", class_="tit").text

    html_transact_date =  soup.find("div", class_="proceed").find("span", class_="day").text.split("~")
    transact_date = html_transact_date[0] if len(html_transact_date) == 1 else html_transact_date[1]
    transact_date = datetime.strptime(re.findall(".+?[.].+?[.].+?[()]", transact_date)[0].strip(),"%Y. %m. %d(",)

    paging_elements = soup.find("div", 'allPageMoving1').find_all('a')
    last_page_element = paging_elements[-1]
    parsed_url = urlparse(last_page_element.get('href'))
    query_params = parse_qs(parsed_url.query)
    number_item_want_to_get = query_params.get("list_scale", [""])[0]
    last_index_item = query_params.get("list", [""])[0]

    total_item = int(number_item_want_to_get) + int(last_index_item)

    url_list = []
    total_item_url = driver.current_url+f"&list_scale={total_item}"
    driver.get(total_item_url)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    for i in soup.find("div", class_='checkerBoard').find_all("li"):
        inbox_element = i.find('div', 'inbox')

        img = inbox_element.find('a').find('div', 'img').find('img').get('src')
        lot = inbox_element.find('a').find('div', 'lot').find('strong').text.strip()
        title_kor = inbox_element.find('a').find('div', 'name').find('p', 'ty').text.strip()

        artist_element = inbox_element.find('a').find('div', 'name').find_all('p')
        
        artist_kor = ""
        artist_birth = ""
        artist_death = ""
        if len(artist_element) > 1:
            artist_date_element = artist_element[0].find('span')

            match_artist_date = re.findall(r"\d+", artist_date_element.text)
            if len(match_artist_date) == 1:
                artist_birth = match_artist_date[0]
            elif len(match_artist_date) == 2:
                artist_birth = match_artist_date[0]
                artist_death = match_artist_date[1]

            artist_date_element.decompose() # remove span element
            artist_kor = artist_element[0].text.strip()

        imgInfo_element = inbox_element.find('div', 'imgInfo')
        if imgInfo_element:
            size = imgInfo_element.find_all('p')[1].text.strip()
            size, etc = Size(size)
            height = size["height"]
            width = size["width"]
            depth = size["depth"]
        else:
            etc = ''
            height = ''
            width = ''
            depth = ''
        
        # currency = inbox_element.find('div', 'amount').find('p', 'stit').find('span').text
        # currency = re.search(r'[a-zA-Z\s]+', currency).group()
        estimate_list = []
        start_price = nan
        price_elements =  inbox_element.find('div', 'amount').find_all('p')
        start_price, estimate_min, estimate_max, hammer_price = nan, nan, nan, nan

        estimate_list = price_elements[1].text.split('~')
        for i in range(len(price_elements)):
            text_element = price_elements[i].text.strip()
            if "시작가" in text_element:
                start_price = price_elements[i + 1].text
                start_price = re.sub("[^[0-9]","", start_price) 
            if price_elements[i].get('class') and 'sblue' in price_elements[i].get('class'):
                hammer_price = re.sub("[^[0-9]","", text_element)

        bid_element = soup.find("div", class_="amount")
        if bid_element:
            hammer_price_element = bid_element.find("div", class_="bid").find("p", class_="price")
            if hammer_price_element:
                hammer_price = re.sub("[^0-9]", "", hammer_price_element.text.strip())


        if len(estimate_list) > 0:
            estimate_min = re.sub("[^[0-9]","", estimate_list[0].strip()) 
            estimate_max = re.sub("[^[0-9]","", estimate_list[1].strip())

        df["description"].append(etc)
        df["lot"].append(lot)
        df["img"].append("https://www.insaauction.com" + img)
        df["artist_kor"].append(artist_kor)
        df["artist_eng"].append('')
        df["title_kor"].append(title_kor)
        df["title_eng"].append('')
        df["artist_death"].append(artist_death)
        df["artist_birth"].append(artist_birth)
        df["material_kor"].append('')
        df["material_eng"].append('')
        df["material_kind"].append('')
        df["height"].append(height)
        df["width"].append(width)
        df["depth"].append(depth)
        df["mfg_date"].append('')
        df["frame"].append('')
        df["estimate_min"].append(estimate_min)
        df["estimate_max"].append(estimate_max)
        df["start_price"].append(start_price)
        df["hammer_price"].append(hammer_price)
        df["signed"].append('')
        df["certification"].append('')
        df["competition"].append('')
        df["selling_price"].append('')
    # print(len(url_list))
    # for url,category in zip(card_url, category_list):
    #     url_list = Card(driver, url)
    #     temp = Detail(driver, url_list)
    #     if category:
    #         temp["material_kind"] = category
    #     df = pd.concat([df, temp], ignore_index=True)

    # # 경매명
    df["auction_name"] = auction_name
    # # 거래년도
    df["transact_date"] = transact_date
    df["company"] = "아이옥션"
    # df["on_off"] = kind
    df["currency"] = "KRW"
    df["location"] = "Korea"

    return pd.DataFrame(df)
        
def main(driver, df):
    login(driver)

    while True:
        print("-" * 20)
        print("1 : offline\n2 : online\n3: 과거경매\nq : 뒤로가기")
        print("-" * 20)
        answer = input("번호를 입력하세요 : ")
        if answer == "1":
            driver.get("https://www.insaauction.com/auction/offline_ing_list.html")
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                al = driver.switch_to.alert
                al.accept()
                print("진행중인 경매가 없습니다.")
            except:
                kind = "offline"
                break
        elif answer == "2":
            driver.get("https://www.insaauction.com/auction/online_ing_list.html")
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                al = driver.switch_to.alert
                al.accept()
                print("진행중인 경매가 없습니다.")
            except:
                kind = "online"
                break
        elif answer == "3":
            while True:
                url = input("url을 입력하세요. (뒤로가기:q) :")
                if "Major" in url or "Market" in url:
                    kind = "offline"
                    break
                elif "Icontact" in url:
                    kind = "online"
                    break
                elif "q" == url:
                    logout(driver)
                    return None, None
            driver.get(url)
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            auction_name = soup.find("div", class_="proceed").find("p", class_="tit").text
            
            # for i in soup.find("div",class_="checkerBoard").find_all("li",{"style":"height: 130px;"}):
            #     lot = int(i.find("div",class_="lot").text)
            #     winning_bid = re.sub("[^0-9.]","",i.find("div",class_="krw").text)
            #     if winning_bid:
            #         print("update crawling set hammer_price={0}, selling_price = {0} * 1.165  where company = '아이옥션' and auction_name = '{1}' and lot = {2};".format(winning_bid, auction_name, lot))
            #         print("update crawling_v1 set hammer_price={0}, selling_price = {0} * 1.165 where company = '아이옥션' and auction_name = '{1}' and lot = {2};".format(winning_bid, auction_name, lot))

            df = handle_crawl_past_with_url(soup, driver)
            df["on_off"] = kind
            logout(driver)
            return df, kind
        elif answer == "q":
            logout(driver)
            return None, None
        else:
            print("보기의 번호를 제대로 입력해주세요.")

    print("데이터 수집 중...")

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    card_url = []
    category_list = []
    if soup.find("div", class_="productCategory"):
        for li in soup.find("div", class_="productCategory").find_all("li"):
            category = "https://www.insaauction.com" + re.sub(
                "list_scale=20", "list_scale=100", li.find("a").get("href")
            )
            card_url.append(category)
            if re.findall("도자|공예", category):
                category_list.append("Sculpture")
            else: category_list.append("")
    else:
        card_url = [driver.current_url+"?list_scale=100"]
        category_list.append("")

    auction_name = soup.find("div", class_="proceed").find("p", class_="tit").text

    html_transact_date =  soup.find("div", class_="proceed").find("span", class_="day").text.split("~")
    transact_date = html_transact_date[0] if len(html_transact_date) == 1 else html_transact_date[1]
    transact_date = datetime.strptime(re.findall(".+?[.].+?[.].+?[()]", transact_date)[0].strip(),"%Y. %m. %d(",)
        

    

    for url,category in zip(card_url, category_list):
        url_list = Card(driver, url)
        temp = Detail(driver, url_list)
        if category:
            temp["material_kind"] = category
        df = pd.concat([df, temp], ignore_index=True)

    # 경매명
    df["auction_name"] = auction_name
    # 거래년도
    df["transact_date"] = transact_date
    df["company"] = "아이옥션"
    df["on_off"] = kind
    df["currency"] = "KRW"
    df["location"] = "Korea"

    logout(driver)
    return df, kind
