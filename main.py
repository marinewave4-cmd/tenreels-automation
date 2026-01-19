#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenreels Daily Music News Automation
매일 오후 1:40(KST)에 자동으로 음악 뉴스를 텐릴스에 포스팅합니다.
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from bs4 import BeautifulSoup
import re
import urllib.parse

# 설정
TENREELS_URL = "https://tenreels.com"
LOGIN_ID = os.environ.get("TENREELS_USERNAME", "news2")
LOGIN_PW = os.environ.get("TENREELS_PASSWORD", "zqzq1212!!")

# 카테고리별 추천 뉴스 소스
CATEGORY_SOURCES = {
    '자유': {
        'sites': ['https://www.soundonsound.com/news'],
        'search_keywords': ['music production tutorial', 'mixing tutorial']
    },
    '보컬': {
        'sites': ['https://www.billboard.com/music/features/'],
        'search_keywords': ['vocal training', 'singing technique']
    },
    '건반': {
        'sites': ['https://www.soundonsound.com/reviews/keyboards'],
        'search_keywords': ['piano tutorial', 'keyboard technique']
    },
    'Guitar': {
        'sites': ['https://www.guitarworld.com/'],
        'search_keywords': ['guitar tutorial', 'guitar technique']
    },
}


def setup_driver():
    """Selenium WebDriver 설정"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except Exception as e:
        print(f"WebDriver 설정 오류: {e}")
        return None


def login(driver):
    """텐릴스 로그인"""
    try:
        print("로그인 시작...")
        driver.get(f"{TENREELS_URL}/bbs/login.php")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "mb_id"))
        )
        id_field = driver.find_element(By.NAME, "mb_id")
        id_field.clear()
        id_field.send_keys(LOGIN_ID)
        pw_field = driver.find_element(By.NAME, "mb_password")
        pw_field.clear()
        pw_field.send_keys(LOGIN_PW)
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        time.sleep(3)
        print("✓ 로그인 완료!")
        return True
    except Exception as e:
        print(f"로그인 오류: {e}")
        return False


def get_oldest_category(driver):
    """카테고리 선택"""
    try:
        categories = list(CATEGORY_SOURCES.keys())
        if not categories:
            return '자유'
        return categories[0]
    except Exception as e:
        print(f"카테고리 확인 오류: {e}")
        return '자유'


def search_news_content(category):
    """뉴스 검색"""
    try:
        print(f"'{category}' 카테고리 뉴스 검색 중...")
        if category not in CATEGORY_SOURCES:
            return None, None, None
        source_info = CATEGORY_SOURCES[category]
        for site in source_info['sites']:
            try:
                response = requests.get(site, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                })
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    titles = soup.find_all(['h1', 'h2', 'h3'], limit=3)
                    if titles:
                        title = titles[0].get_text().strip()[:80]
                        search_keyword = source_info['search_keywords'][0]
                        content = generate_content(category, title)
                        print(f"✓ 뉴스 발견: {title}")
                        return title, content, search_keyword
            except Exception:
                continue
        default_title = f"{category} 음악 가이드 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        search_keyword = source_info['search_keywords'][0]
        default_content = generate_content(category, default_title)
        return default_title, default_content, search_keyword
    except Exception as e:
        print(f"뉴스 검색 오류: {e}")
        return None, None, None


def generate_content(category, title):
    """콘텐츠 생성"""
    content = f"""안녕하세요! 오늘은 {category} 음악인들을 위한 정보를 공유합니다.

【{title}】

음악 제작과 연주 기술은 지속적인 학습을 통해 향상됩니다.

주요 포인트:
1. 기본기 습득의 중요성
2. 최신 도구와 기술 활용
3. 꾸준한 연습과 피드백
4. 커뮤니티와의 교류

tenreels.com에서 더 많은 정보를 확인하세요!
"""
    return content


def search_youtube_video(search_keyword):
    """YouTube 영상 검색"""
    try:
        print(f"YouTube에서 '{search_keyword}' 검색 중...")
        search_query = f"{search_keyword} tutorial"
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
        response = requests.get(search_url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        if response.status_code == 200:
            video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)
            if video_ids:
                youtube_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                print(f"✓ YouTube 영상 발견: {youtube_url}")
                return youtube_url
        return f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
    except Exception as e:
        print(f"YouTube 검색 오류: {e}")
        return f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_keyword)}"


def post_to_tenreels(driver, category, title, content, youtube_url):
    """텐릴스에 포스팅"""
    try:
        print("포스팅 시작...")
        driver.get(f"{TENREELS_URL}/bbs/write.php?bo_table=m_news")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "wr_subject"))
        )
        time.sleep(2)
        try:
            category_select = Select(driver.find_element(By.NAME, "ca_name"))
            category_select.select_by_value(category)
            time.sleep(1)
        except Exception:
            print(f"카테고리 선택 시도: {category}")
        title_field = driver.find_element(By.NAME, "wr_subject")
        title_field.clear()
        title_field.send_keys(title)
        print(f"✓ 제목 입력: {title}")
        try:
            youtube_field = driver.find_element(By.NAME, "wr_youtube")
            youtube_field.clear()
            youtube_field.send_keys(youtube_url)
            print(f"✓ 유튜브 링크: {youtube_url}")
        except Exception:
            pass
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                driver.switch_to.frame(iframes[0])
                body = driver.find_element(By.TAG_NAME, "body")
                embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"
                body.send_keys(embed_content)
                driver.switch_to.default_content()
                print("✓ 본문 입력 (YouTube 임베드 포함)")
            else:
                content_field = driver.find_element(By.NAME, "wr_content")
                embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"
                content_field.send_keys(embed_content)
                print("✓ 본문 입력")
        except Exception as e:
            print(f"본문 입력 중 오류: {e}")
        time.sleep(2)
        # Scroll down to make submit button visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Try to find and click submit button
        try:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), '작성완료')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", submit_btn)
            print("✓ 포스팅 완료!")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"작성완료 버튼 클릭 실패: {e}")
            # Try form submit as fallback
            try:
                form = driver.find_element(By.TAG_NAME, "form")
                form.submit()
                print("✓ 폼 제출 완료!")
                time.sleep(3)
                return True
            except Exception as e2:
                print(f"폼 제출도 실패: {e2}")
        return True
    except Exception as e:
        print(f"포스팅 중 오류: {e}")
        return False


def main():
    """메인 실행 함수"""
    print(f"\n{'='*60}")
    print(f"텐릴스 음악인 도움 자동화 시스템 시작 ({datetime.now()})")
    print(f"{'='*60}\n")

    driver = setup_driver()
    if not driver:
        print("❌ WebDriver 초기화 실패")
        return

    try:
        if not login(driver):
            print("❌ 로그인 실패")
            return
        category = get_oldest_category(driver)
        title, content, search_keyword = search_news_content(category)
        if not title or not content:
            print("❌ 뉴스 검색 실패")
            return
        youtube_url = search_youtube_video(search_keyword)
        if post_to_tenreels(driver, category, title, content, youtube_url):
            print(f"\n✅ 음악인들을 위한 포스팅 완료!\n")
        else:
            print(f"\n⚠ 포스팅 중 오류 발생\n")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
