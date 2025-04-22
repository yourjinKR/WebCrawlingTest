from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time

# 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

# 웹 드라이버 실행
driver = webdriver.Chrome(options=options)

# URL 접속
url = "https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do"
driver.get(url)

# 페이지 로딩 대기
time.sleep(3)  # 필요에 따라 조정

# 축제 정보를 담고 있는 요소들 수집
festival_elements = driver.find_elements(By.CSS_SELECTOR, ".other_festival_content")

# 데이터 수집
festival_data = []

for fest in festival_elements:
    try:
        name = fest.find_element(By.TAG_NAME, "strong").text.strip()
        date = fest.find_element(By.CSS_SELECTOR, ".date").text.strip()
        location = fest.find_element(By.CSS_SELECTOR, ".loc").text.strip()
        festival_data.append([name, date, location])
    except Exception as e:
        print(f"에러 발생: {e}")

# CSV 파일로 저장
with open("festivals.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["축제명", "날짜", "장소"])
    writer.writerows(festival_data)

print("크롤링 완료 및 CSV 저장 완료")
