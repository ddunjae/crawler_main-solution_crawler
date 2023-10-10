import re
from itertools import product
import pandas as pd


def artist_define():
     data = [
          ["윤형근", "Yun HyongKeun", "1928", "2007"],
          ["김환기", "Kim WhanKi", "1928", "1974"],
          ["정상화", "Chung SangHwa", "1932", ""],
          ["김창열", "Kim TschangYeul", "1929", "2021"],
          ["박서보", "Park SeoBo", "1931", ""],
          ["이성자", "Rhee SeundJa", "1918", "2009"],
          ["이우환", "Lee UFan", "1936", ""],
          ["이응노", "Lee UngNo", "1904", "1989"],
          ["남관", "Nam Kwan", "1911", "1990"],
          ["이배", "Lee Bae", "1956", ""],
          ["김종학", "Kim ChongHak", "1937", ""],
          ["이강소", "Lee KangSo", "1943", ""],
          ["백남준", "Paik NamJune", "1932", "2006"],
          ["오치균", "Oh ChiGyun", "1956", ""],
          ["김구림", "Kim KuLim", "1936", ""],
          ["이건용", "Lee KunYong", "1942", ""],
          ["권영우", "Kwon YoungWoo", "1926", "2013"],
          ["서세옥", "Suh SeOk", "1929", "2020"],
          ["유영국", "Yoo YoungKuk", "1916", "2002"],
          ["곽인식", "Quac InSik", "1919", "1988"],
          ["하종현", "Ha ChongHyun", "1935", ""],
          ["문신", "Moon Shin", "1923", "1995"],
          ["서도호", "Suh DoHo", "1962", ""],
          ["양혜규", "Yang HaeGue", "1971", ""],
          ["박수근", "Park SooKeun", "1914", "1965"],
          ["이중섭", "Lee JungSeop", "1916", "1956"],
          ["심문섭", "Shim MoonSeup", "1943", ""],
          ["남춘모", "Nam TchunMo", "1961", ""],
          ["도상봉", "To SangBong", "1902", "1977"],
          ["허황", "Her Hwang", "1946", ""],
          ["전혁림", "Chun HyuckLim", "1916", "2010"],
          ["장리석", "Chang ReeSuk", "1916", "2019"],
          ["이희돈", "Lee HuiDon", "1950", ""],
          ["이승조", "Lee SeungJio", "1941", "1990"],
          ["이동엽", "Lee DongYoub", "1946", "2013"],
          ["윤명로", "Youn Myeung-Ro", "1936", ""],
          ["야요이 쿠사마", "Yayoi Kusama", "1929", ""],
          ["타카시 무라카미", "Takashi Murakami", "1962", ""],
          ["아야코 록카쿠", "Ayako Rokkaku", "1982", ""],
          ["치하루 시오타", "Chiharu Shiota", "1972", ""],
          ["요시토모 나라", "Yoshitomo Nara", "1959", ""],
          ["데이비드 거스타인", "David Gerstein", "1944", ""],
          ["캐서린 번하드", "Katherine Bernhardt", "1975", ""],
     ]
     df = pd.DataFrame(data, columns=['artist_kor','artist_eng','born','dead'])
     return df
     



def convert_KRname():
    return {
            "윤" : ["Yun", "Yoon", "Youn"],
            "형" : ["Hyong", "Hyung", "Hyeong"],
            "근" : ["Geun", "Keun", "Kun"],
            "환" : ["Whan", "Hwan", "Fan"],
            "정" : ["Chung", "Jeong", "Jung"],
            "창" : ["Tschang", "Chang"],
            "장" : ["Chang", "Jang"],
            "서" : ["Seo", "Suh"],
            "이" : ["Rhee", "Lee", "Li", "Yi", "Ree"],
            "열" : ["Yeul", "Yeol"],
            "백" : ["Paik", "Paek", "Baek"],
            "성" : ["Seund", "Sung", "Seong"],
            "응" : ["Ung", "Eung"],
            "노" : ["No", "Ro"],
            "조" : ["Jio", "Jo"],
            "엽" : ["Youb", "Yeop", "Yeob", "Yeup"],
            "구" : ["Ku", "Gu"],
            "종" : ["Chong", "Jong"],
            "준" : ["June", "Joon", "Jun"],
            "균" : ["Gyun", "Kyun"],
            "림" : ["Lim", "Rim"],
            "국" : ["Kuk", "Gkuk"],
            "곽" : ["Quac", "Kwak"],
            "문" : ["Moon", "Mun"],
            "수" : ["Soo", "Su"],
            "중" : ["Jung", "Joong"],
            "섭" : ["Seup", "Sub", "Seob", "Sup", "Seop"],
            "도" : ["To", "Do"],
            "허" : ["Her", "Heu", "Huh"],
            "춘" : ["Tchun", "Chun"],
            "석" : ["Suk", "Suok", "Seok"],
            "희" : ["Hui", "Hee"],
            "혁" : ["Hyuck", "Hyuk"],
            "심" : ["Shim", "Sim"],
            "명" : ["Myeung", "Myung", "Myeong"],
            }


def convert_ENname():
    return {
            "Bernhardt" : ["번하드","버나드","베른하르트"],
            "Kusama" : ["구사마", "쿠사마"],
            "Takashi" : ["타카시", "다카시"],
            "Rokkaku" : ["로카쿠","록카쿠"],
            "Gerstein" : ["거스타인","걸스타인"],
            }


def define_artist(lang):
    if lang == "kor":
            artist_name = {
            "야요이 쿠사마" : [],
            "타카시 무라카미" :[],
            "아야코 록카쿠" : [],
            "치하루 시오타" : [],
            "요시토모 나라" : [],
            "데이비드 거스타인" : [],
            "캐서린 번하드" : []
            }
    if lang == "eng":
            artist_name = {
            "Yun HyuongKeun" : [],
            "Kim WhanKi" :[],
            "Chung SangHwa" : [],
            "Kim TschangYeul" : [],
            "Park SeoBo" : [],
            "Rhee SeundJa" : [],
            "Lee UFan" : [],
            "Lee UngNo" : [],
            "Nam Kwan" : [],
            "Lee Bae" : [],
            "Kim ChongHak" : [],
            "Lee KangSo" : [],
            "Paik NamJune" : [],
            "Oh ChiGyun" : [],
            "Kim KuLim" : [],
            "Lee KunYong" : [],
            "Kwon YoungWoo" : [],
            "Suh SeOk" : [],
            "Yoo YoungKuk" : [],
            "Quac InSik" : [],
            "Ha ChongHyun" : [],
            "Moon Shin" : [],
            "Suh DoHo" : [],
            "Yang HaeGue" : [],
            "Park SooKeun" : [],
            "Lee JungSeop" : [],
            "Shim MoonSeup" : [],
            "Nam TchunMo" : [],
            "To SangBong" : [],
            "Her Hwang" : [],
            "Chun HyuckLim" : [],
            "Chang ReeSuk" : [],
            "Lee HuiDon" : [],
            "Lee SeungJio" : [],
            "Lee DongYoub" : [],
            "Youn Myeung-Ro" : [],
            "Yayoi Kusama" : [],
            "Takashi Murakami" : [],
            "Ayako Rokkaku" : [],
            "Chiharu Shiota" : [],
            "Yoshitomo Nara" : [],
            "David Gerstein" : [],
            "Katherine Bernhardt" : []
        }
    # for key in artist_name.keys():
    #     artist_name[key].append(re.sub(" ","",key))
    #     first_name = ""
    #     last_name = ""
    #     if len(key.split()) >= 2:
    #         last_name = "".join(key.split()[1:])
    #         first_name = key.split()[0]
    #     else:
    #         first_name = artist_name[key].strip()
    #     artist_name[key].extend(combination_name(first_name + last_name))
    #     artist_name[key].extend(combination_name(last_name + first_name))
    # return artist_name