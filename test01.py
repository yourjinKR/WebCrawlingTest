from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time

# 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

# 드라이버 실행
driver = webdriver.Chrome(options=options)
url = "https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do"
driver.get(url)

# 데이터 수집용 리스트
festival_data = []

# 축제 요소 누적 수를 체크하여 100개 이상이 될 때까지 스크롤
SCROLL_PAUSE_TIME = 1
MAX_COUNT = 100
prev_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # 현재까지 로드된 축제 요소들 가져오기
    elements = driver.find_elements(By.CSS_SELECTOR, ".other_festival_content")

    # 수집한 개수가 100개 이상이면 멈춤
    if len(elements) >= MAX_COUNT:
        break

    # 스크롤 맨 아래로 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    # 스크롤 후 높이 확인
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        print("더 이상 스크롤되지 않음")
        break
    prev_height = new_height

print(f"{len(elements)}개의 축제 정보 로드됨")

# 상위 100개의 축제 정보 수집
for fest in elements[:100]:
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

print("스크롤 완료 및 CSV 저장 완료")
