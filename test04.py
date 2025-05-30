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
        return date_str  # 실패 시 원본 유지

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
        
        # ▶ "내용글" 수집: 기본 내용 + 더보기 확장 내용 포함
        try:
            content_element = driver.find_element(By.CSS_SELECTOR, ".slide_content.fst")

            # ▣ 더보기 클릭 및 내용 추가 (삭제 전에 해야 함)
            try:
                more_btn = content_element.find_element(By.CSS_SELECTOR, ".more_pc_btn")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(0.5)
                more_content = get_text(".m_more")
                print("더보기 정보 수집")
            except:
                more_content = ""

            # ▣ 버튼 제거 (텍스트 수집 전 제거해야 "더보기"가 포함되지 않음)
            try:
                btn = content_element.find_element(By.CSS_SELECTOR, ".more_pc_btn")
                driver.execute_script("arguments[0].remove();", btn)
            except:
                pass

            # ▣ 텍스트 추출
            content = content_element.text.strip()

            # ▣ 더보기 내용 합치기
            if more_content:
                content += "\n" + more_content

        except:
            content = ""

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
        
        # ▣ 시작일과 종료일 분리
        raw_period = infos[0].text.strip() if len(infos) > 0 else ""
        start_date, end_date = "", ""
        if " ~ " in raw_period:
            parts = raw_period.split(" ~ ")
            if len(parts) == 2:
                start_date = parts[0].strip()
                end_date = parts[1].strip()
                start_date = normalize_date(start_date)
                end_date = normalize_date(end_date)
        else:
            # 하루짜리인 경우 시작일 = 종료일 동일하게 처리
            start_date = end_date = raw_period        
        address = infos[1].text.strip() if len(infos) > 1 else ""
        agency = infos[3].text.strip() if len(infos) > 3 else ""
        contact = infos[4].text.strip() if len(infos) > 4 else ""

        # ▣ 데이터 저장
        festival_data.append([
            name, sub_title, content, detail, poster_img,
            image_links[0], image_links[1], image_links[2],
            start_date, end_date, address, agency, contact
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
        "이미지1", "이미지2", "이미지3", "시작일", "종료일", "주소", "운영기관", "연락처"
    ])
    writer.writerows(festival_data)

print("✅ 크롤링 완료 (뒤로가기 방식)")