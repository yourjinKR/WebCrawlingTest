from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time
import re
from datetime import datetime

# 날짜 포맷팅
def normalize_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y.%m.%d").strftime("%Y-%m-%d")
    except:
        return date_str

# 브라우저 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# 페이지 접속
driver.get("https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do")
time.sleep(2)

# 스크롤 함수
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

# 수집할 축제 수
target_count = 100
festival_data = []
idx = 0

while len(festival_data) < target_count:
    try:
        scroll_until(min_count=idx + 1)
        festival_elements = driver.find_elements(By.CSS_SELECTOR, "ul.other_festival_ul li a")
        if idx >= len(festival_elements):
            print(f"[❗] index {idx}가 범위를 벗어났습니다.")
            break

        link_element = festival_elements[idx]
        temp_name = link_element.text.strip()
        link_element.click()
        time.sleep(1.5)

        def get_text(selector):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                return ""

        name = get_text("#festival_head")
        sub_title = get_text(".sub_title")

        try:
            content_element = driver.find_element(By.CSS_SELECTOR, ".slide_content.fst")
            try:
                more_btn = content_element.find_element(By.CSS_SELECTOR, ".more_pc_btn")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(0.5)
                more_content = get_text(".m_more")
                print("더보기 정보 수집")
            except:
                more_content = ""

            try:
                btn = content_element.find_element(By.CSS_SELECTOR, ".more_pc_btn")
                driver.execute_script("arguments[0].remove();", btn)
            except:
                pass

            content = content_element.text.strip()
            if more_content:
                content += "\n" + more_content
        except:
            content = ""

        detail = get_text(".slide_content.lst")

        try:
            poster_img = driver.find_element(By.CSS_SELECTOR, ".detail_img_box img").get_attribute("src")
        except:
            poster_img = ""

        image_links = []
        imgs = driver.find_elements(By.CSS_SELECTOR, ".swiper-slide a.imgClick")
        for img in imgs[:3]:
            style = img.get_attribute("style")
            match = re.search(r'url\(["\']?(https?://[^\s"\')]+)', style)
            image_links.append(match.group(1) if match else "")
        while len(image_links) < 3:
            image_links.append("")

        infos = driver.find_elements(By.CSS_SELECTOR, "p.info_content")
        raw_period = infos[0].text.strip() if len(infos) > 0 else ""
        start_date, end_date = "", ""
        if " ~ " in raw_period:
            parts = raw_period.split(" ~ ")
            if len(parts) == 2:
                start_date = normalize_date(parts[0].strip())
                end_date = normalize_date(parts[1].strip())
        else:
            start_date = end_date = normalize_date(raw_period)

        address = infos[1].text.strip() if len(infos) > 1 else ""
        agency = infos[3].text.strip() if len(infos) > 3 else ""
        contact = infos[4].text.strip() if len(infos) > 4 else ""

        festival_data.append([
            name, sub_title, content, detail, poster_img,
            image_links[0], image_links[1], image_links[2],
            start_date, end_date, address, agency, contact
        ])

        print(f"[✔] {idx} - {name or temp_name} 수집 완료")

        driver.back()
        time.sleep(1.5)
        idx += 1

    except Exception as e:
        print(f"[에러] index {idx} - {e}")
        driver.back()
        time.sleep(1.5)
        idx += 1

# CSV 저장
with open("festival_detail_100_by_back.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "축제명", "간단한 소개", "내용글", "상세내용", "포스터 이미지",
        "이미지1", "이미지2", "이미지3", "시작일", "종료일", "주소", "운영기관", "연락처"
    ])
    writer.writerows(festival_data)

print("✅ 크롤링 완료 (100개)")
