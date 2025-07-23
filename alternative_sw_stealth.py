import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random


def get_software_url(software):
    return f"https://alternativeto.net/software/{software}/"


def safe_get(driver, url, retries=3, wait_sec=10):
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"[경고] 페이지 로딩 실패({i+1}/{retries}): {e}")
            time.sleep(wait_sec)
    return False


def collect_alternative_links(driver, base_url):
    wait = WebDriverWait(driver, 30)
    all_links = set()
    page_num = 1
    while True:
        if page_num == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}?p={page_num}"
        print(f"페이지 방문: {page_url}")
        if not safe_get(driver, page_url):
            print(f"[경고] {page_url} 로딩 실패, 건너뜀")
            break
        time.sleep(random.uniform(1, 3))
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-testid^=\"item-\"]')))
            items = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid^=\"item-\"]')
        except Exception as e:
            print(f"[경고] 항목 리스트 탐색 실패: {e}")
            break
        if not items:
            print(f"페이지 {page_num}에 항목이 없습니다. 종료합니다.")
            break
        for item in items:
            try:
                name_elem = item.find_element(By.CSS_SELECTOR, 'h2')
                name = name_elem.text.strip()
                link_elem = item.find_element(By.CSS_SELECTOR, 'a[href*=\"/software/\"][href$=\"/about/\"]')
                link = link_elem.get_attribute('href')
                all_links.add((name, link))
            except Exception as e:
                print(f"[경고] 링크 파싱 실패: {e}")
            time.sleep(random.uniform(0.5, 1.2))
        page_num += 1
    print(f"총 {len(all_links)}개 대안 소프트웨어 링크 수집 완료!")
    return all_links


def parse_alternative_info(driver, all_links):
    wait = WebDriverWait(driver, 30)
    all_alt_data = []
    for idx, (name, link) in enumerate(all_links, 1):
        if link.endswith('/about/'):
            about_url = link
        else:
            about_url = link.rstrip('/') + '/about'
        print(f"{idx}/{len(all_links)}: {about_url} 정보 파싱 중...")
        try:
            if not safe_get(driver, about_url):
                print(f"[경고] {about_url} 로딩 실패, 건너뜀")
                continue
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
            name_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
            desc_elem = driver.find_elements(By.CSS_SELECTOR, 'div[itemprop=\"description\"]')
            desc = desc_elem[0].text.strip() if desc_elem else ''
            platforms = [span.text.strip() for span in driver.find_elements(By.CSS_SELECTOR, 'ul[data-testid="platform-row"] li span')]
            # Official Website 및 GitHub 링크 추출
            official_website = ''
            github = ''
            external_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="external-link"]')
            for a in external_links:
                try:
                    btns = a.find_elements(By.TAG_NAME, 'button')
                    for btn in btns:
                        if 'Official Website' in btn.text:
                            official_website = a.get_attribute('title') or a.get_attribute('href')
                    href = a.get_attribute('href')
                    if href and 'github.com' in href:
                        github = href
                except Exception:
                    continue
            info = {
                'name': name_elem.text.strip() if name_elem else name,
                'link': about_url,
                'description': desc,
                'platforms': platforms,
                'official_website': official_website,
                'github': github
            }
            all_alt_data.append(info)
        except Exception as e:
            print(f"[경고] {about_url} 파싱 실패: {e}")
        time.sleep(random.uniform(2, 5))
    print(f"총 {len(all_alt_data)}개 대안 소프트웨어 정보 저장 완료!")
    return all_alt_data


def crawl_alternativeto_software_alternatives(software):
    base_url = get_software_url(software)
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument('--headless')  # 필요시 headless 모드 사용
    with uc.Chrome(options=options) as driver:
        if not safe_get(driver, base_url):
            print(f"[경고] {base_url} 로딩 실패, 종료")
            return
        all_links = collect_alternative_links(driver, base_url)
        all_alt_data = parse_alternative_info(driver, all_links)
        with open(f'{software}_alternatives.json', 'w', encoding='utf-8') as f:
            json.dump(all_alt_data, f, ensure_ascii=False, indent=2)
        print(f"총 {len(all_alt_data)}개 대안 소프트웨어 정보 저장 완료! 파일명: {software}_alternatives.json")


if __name__ == "__main__":
    # 예시: software='snaptube'로 실행
    crawl_alternativeto_software_alternatives('snaptube') 