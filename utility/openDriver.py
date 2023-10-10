import platform
from selenium import webdriver
import os

def open_driver():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    try:
        driver = webdriver.Chrome(path, options=options)
        options.add_argument("headless")
        driver2 = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver, driver2


def open_driver_visu():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

##########################
# 1단
##########################
def open_driver_KArtMarket():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket1():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub1',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket2():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub2',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket3():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub3',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver



##########################
# 2단
##########################
def open_driver_KArtMarket_():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket1_():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub1_',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket2_():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub2_',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver

def open_driver_KArtMarket3_():
    # 웹브라우져로 크롬을 사용할거라서 크롬 드라이버를 다운받아 폴더에 저장함
    if platform.system() == "Darwin":
        path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        in_dir = "/"
    else:
        path = os.path.dirname(os.path.realpath(__file__)) + "\chromedriver.exe"
        in_dir = "\\"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    )
    # options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': '/Users/settong/yeolmae/auction_analysis/auction_crawler/kartmarket_img_sub3_',
        'download.prompt_for_download': False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    try:
        driver = webdriver.Chrome(path, options=options)
    except:
        print("Error : 프로그램을 종료합니다.")
        print(
            "확인내용 :\n1. 디렉토리("
            + os.path.realpath(__file__)
            + ")에 chromedriver가 없음\n 디렉토리내에 chromedriver를 설치해주세요."
        )
        print(
            "2. 사용 중인 chrome버전이 아님\n디렉토리("
            + os.path.realpath(__file__)
            + ")내의 chromedriver를 chrome 버전에 맞게 대체해주세요. "
        )
        print("3. 리눅스 운영체제임\n리눅스는 사용할 수 없습니다.")
        quit()
    return driver