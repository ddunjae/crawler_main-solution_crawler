from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdfkit
import os
import time

# wkhtmltopdf 실행 파일 경로 설정
wkhtmltopdf_path = '/usr/local/bin/wkhtmltopdf'  # 이 경로를 실제 경로로 수정하세요.

# pdfkit 옵션 설정 (크롬 드라이버 경로 및 브라우저 무료 모드 등)
pdfkit_options = {
    'no-images': True,  # 이미지를 불러오지 않음 (선택 사항)
}

# Chrome WebDriver 경로 설정
chrome_driver_path = '/Users/hanseungjae/auction_solution/crawler-main/utility/chromedriver'

# 웹 브라우저 옵션 설정
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 브라우저를 화면에 표시하지 않음

# 웹 드라이버 초기화
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

# 페이지 URL 설정
base_url = 'https://static-image-server.s3.ap-northeast-2.amazonaws.com/20230811-085541-35574669/index.html'

# 웹 페이지 열기
driver.get(base_url)

# "class='wnd main'" 안에 있는 "class='btn thumb'" 클릭
try:
    wnd_main = driver.find_element_by_css_selector('div.wnd.main')
    thumb_button = wnd_main.find_element_by_css_selector('div.btn.thumb')
    thumb_button.click()
except Exception as e:
    print(f'메인 페이지에서 썸네일 버튼을 찾을 수 없습니다. 에러: {str(e)}')

# 임시 디렉터리 생성
temp_dir = '/Users/hanseungjae/auction_solution/crawler-main/utility/temp'
os.makedirs(temp_dir, exist_ok=True)

# PDF 파일 경로 설정
pdf_dir = '/Users/hanseungjae/auction_solution/crawler-main/utility/pdf'
os.makedirs(pdf_dir, exist_ok=True)

# 페이지 번호 초기화
page_number = 1

while True:
    # 스크린샷 찍기
    screenshot_file_path = os.path.join(temp_dir, f'screenshot_page_{page_number}.png')
    driver.save_screenshot(screenshot_file_path)
    print(f'페이지 {page_number}의 스크린샷을 찍었습니다.')

    # 각 스크린샷을 개별 PDF 파일로 저장
    pdf_file_path = os.path.join(pdf_dir, f'page_{page_number}.pdf')
    pdfkit.from_file(screenshot_file_path, pdf_file_path, options=pdfkit_options,
                     configuration=pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path))

    # "class='btn next'"를 찾아 클릭하여 다음 페이지로 이동
    try:
        next_button = driver.find_element_by_css_selector('div.btn.next')
        next_button.click()
    except Exception as e:
        print(f'페이지 {page_number}에서 다음 버튼을 찾을 수 없습니다. 에러: {str(e)}')
        break

    page_number += 1

    # 스크린샷이 완료될 때까지 잠시 대기 (선택 사항)
    time.sleep(3)  # 3초 대기

# 브라우저 닫기
driver.quit()

print('각 페이지의 스크린샷을 개별 PDF 파일로 저장했습니다.')
