import os
import shutil
import re
import urllib.request
from urllib.parse import quote
import ssl


def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("폴더생성에 실패했습니다.")


def removeDirectory(directory):
    if os.path.exists(directory):
        print("임시폴더 삭제")
        shutil.rmtree(directory)


def toExcel(df, directory, name):
    createDirectory(directory)
    df.to_excel(directory + name, index=False)
    print("경로 : " + directory + "\n파일명 : " + name)


def toJpg(url, directory, name):
    ssl._create_default_https_context = ssl._create_unverified_context
    if type(url) == str:
        if re.search("[ㄱ-ㅣ가-힣]", url):
            url = re.sub("https%3A", "https:", re.sub("http%3A", "http:", quote(url)))
        urllib.request.urlretrieve(url, "{0}/{1}.jpg".format(directory, name))
    else:
        print("url을 확인해주세요 :", url)
