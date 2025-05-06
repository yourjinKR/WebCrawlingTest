from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time
import re

# ▣ 브라우저 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

# ▣ 축제 리스트 페이지 접속
driver.get("https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do")
time.sleep(2)

# ▣ 축제 리스트 충분히 로딩되도록 스크롤 내리기
def scroll_until(min_count=3):
    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        items = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")
        if len(items) >= min_count:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

scroll_until(min_count=3)

# ▣ 수집할 축제 수
target_count = 3

# ▣ 전체 축제 리스트 요소 수집
festival_elements = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")

# ▣ 최종 데이터 저장 리스트
festival_data = []

# ▣ 반복 수집
for idx in range(min(target_count, len(festival_elements))):
    try:
        # ⛳ 리스트 다시 가져오기 (페이지 리로딩 후 요소가 갱신되므로)
        festival_elements = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")
        link_element = festival_elements[idx]

        # 📌 축제명 (a 태그 텍스트로 임시 수집)
        temp_name = link_element.text.strip()

        # ▶ 축제 상세 페이지 이동
        link_element.click()
        time.sleep(1.5)

        # ▣ 텍스트 안전 추출 함수
        def get_text(selector):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                return ""

        # ▣ 정보 수집 시작
        name = get_text("#festival_head")
        sub_title = get_text(".sub_title")
        content = get_text(".slide_content.fst")
        detail = get_text(".slide_content.lst")

        try:
            poster_img = driver.find_element(By.CSS_SELECTOR, ".detail_img_box img").get_attribute("src")
        except:
            poster_img = ""

        # ▣ 이미지 3개 수집
        image_links = []
        imgs = driver.find_elements(By.CSS_SELECTOR, ".swiper-slide a.imgClick")
        for img in imgs[:3]:
            style = img.get_attribute("style")
            match = re.search(r'url\(["\']?(https?://[^\s"\')]+)', style)
            image_links.append(match.group(1) if match else "")
        while len(image_links) < 3:
            image_links.append("")

        # ▣ 기타 정보
        infos = driver.find_elements(By.CSS_SELECTOR, "p.info_content")
        period = infos[0].text.strip() if len(infos) > 0 else ""
        address = infos[1].text.strip() if len(infos) > 1 else ""
        agency = infos[3].text.strip() if len(infos) > 3 else ""
        contact = infos[4].text.strip() if len(infos) > 4 else ""

        # ▣ 데이터 저장
        festival_data.append([
            name, sub_title, content, detail, poster_img,
            image_links[0], image_links[1], image_links[2],
            period, address, agency, contact
        ])

        print(f"[✔] {name or temp_name} 수집 완료")

        # ⬅ 리스트 페이지로 되돌아가기
        driver.back()
        time.sleep(1.5)

    except Exception as e:
        print(f"[에러] index {idx} - {e}")
        driver.back()  # 에러 발생 시에도 이전 페이지 복귀
        time.sleep(1)

# ▣ CSV 저장
with open("festival_detail_3_by_back.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "축제명", "간단한 소개", "내용글", "상세내용", "포스터 이미지",
        "이미지1", "이미지2", "이미지3", "기간", "주소", "운영기관", "연락처"
    ])
    writer.writerows(festival_data)

print("✅ 크롤링 완료 (뒤로가기 방식)")