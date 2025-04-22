from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time
import re

# ▣ Chrome 브라우저 옵션 설정
options = Options()
options.add_argument("--start-maximized")  # 창 최대화
options.add_experimental_option("detach", True)  # 자동 종료 방지

# ▣ 웹 드라이버 실행
driver = webdriver.Chrome(options=options)

# ▣ 축제 목록 페이지 접속
driver.get("https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do")
time.sleep(2)  # 페이지 로딩 대기

# ▣ 축제 리스트가 일정 개수 이상 나올 때까지 스크롤 다운
def scroll_until(min_count=10):
    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 현재까지 로드된 축제 수 확인
        items = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")
        if len(items) >= min_count:
            break
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # 로딩 시간 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break  # 더 이상 로드되지 않으면 종료
        prev_height = new_height

scroll_until(min_count=10)

# ▣ 축제 상세 페이지 링크 추출
links = []
elements = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")
for a in elements:
    href = a.get_attribute("href")
    if href and href.startswith("/kfes/detail/fstvlDetail.do"):
        full_link = "https://korean.visitkorea.or.kr" + href
        if full_link not in links:
            links.append(full_link)  # 중복 제거

# ▣ 수집한 축제 정보 저장용 리스트
festival_data = []

# ▣ 각 축제 상세 페이지에 접속하여 정보 수집
for link in links[:10]:  # 테스트용으로 10개만 진행
    try:
        driver.get(link)
        time.sleep(1)

        # ▣ 텍스트 추출 함수 (에러 방지용)
        def get_text(selector):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                return ""

        # ▣ 각 항목 추출
        name = get_text(".festival_title")  # 축제명
        sub_title = get_text(".sub_title")  # 간단한 소개
        content = get_text(".slide_content.fst")  # 내용글
        detail = get_text("p.slide_content.lst")  # 상세내용

        # ▣ 포스터 이미지 추출
        try:
            poster_img = driver.find_element(By.CSS_SELECTOR, ".detail_img_box img").get_attribute("src")
        except:
            poster_img = ""

        # ▣ 이미지 1~3 추출 (style 속성에서 URL 추출)
        image_links = []
        imgs = driver.find_elements(By.CSS_SELECTOR, ".swiper-slide a.imgClick")
        for img in imgs[:3]:
            style = img.get_attribute("style")
            match = re.search(r'url\((https?://[^\s,)]+)', style)
            image_links.append(match.group(1) if match else "")
        while len(image_links) < 3:
            image_links.append("")  # 3개가 안 될 경우 빈 문자열로 채움

        # ▣ 기타 정보 추출
        period = get_text("div.info_ico.data p.info_content")  # 기간
        address = get_text("div.info_ico.location p.info_content")  # 주소
        agency = get_text("div.info_ico.partner p.info_content")  # 운영기관
        contact = get_text("div.info_ico.tell p.info_content")  # 연락처

        # ▣ 수집한 데이터를 리스트에 저장
        festival_data.append([
            name, sub_title, content, detail, poster_img,
            image_links[0], image_links[1], image_links[2],
            period, address, agency, contact
        ])

        print(f"[✔] {name} 수집 완료")  # 진행 상황 출력

    except Exception as e:
        print(f"[에러] {link}: {e}")  # 예외 발생 시 출력
        continue

# ▣ 수집한 데이터를 CSV 파일로 저장
with open("festival_detail_10.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "축제명", "간단한 소개", "내용글", "상세내용", "포스터 이미지",
        "이미지1", "이미지2", "이미지3", "기간", "주소", "운영기관", "연락처"
    ])
    writer.writerows(festival_data)

print("✅ 10개 축제 데이터 저장 완료 (festival_detail_10.csv)")
# 미작동 코드