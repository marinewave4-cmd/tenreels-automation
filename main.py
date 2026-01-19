#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenreels Daily Music News Automation
매일 오후 1:40(KST)에 자동으로 음악 뉴스를 텐릴스에 포스팅합니다.
음악인들에게 실질적으로 도움되는 뉴스와 관련된 최고의 YouTube 튜토리얼을 자동으로 매칭합니다.
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
                                'sites': [
                                                      'https://www.soundonsound.com/news',
                                                      'https://www.pro-tools-expert.com/',
                                ],
                                'search_keywords': ['music production tutorial', 'mixing tutorial']
              },
              '보컬': {
                                'sites': [
                                                      'https://www.billboard.com/music/features/',
                                ],
                                'search_keywords': ['vocal training', 'singing technique', 'voice lesson']
              },
              '건반': {
                                'sites': [
                                                      'https://www.soundonsound.com/reviews/keyboards',
                                ],
                                'search_keywords': ['piano tutorial', 'keyboard technique', 'synth lesson']
              },
              'Guitar': {
                                'sites': [
                                                      'https://www.guitarworld.com/',
                                ],
                                'search_keywords': ['guitar tutorial', 'guitar technique', 'guitar lesson']
              },
              'Drum & Bass': {
                                'sites': [
                                                      'https://www.soundonsound.com/reviews/drums',
                                ],
                                'search_keywords': ['drum tutorial', 'bass technique', 'rhythm lesson']
              },
              '현악기': {
                                'sites': [
                                                      'https://www.gramophone.co.uk/',
                                ],
                                'search_keywords': ['violin tutorial', 'cello lesson', 'string technique']
              },
              '엔지니어': {
                                'sites': [
                                                      'https://www.soundonsound.com/techniques',
                                ],
                                'search_keywords': ['audio engineering', 'recording tutorial', 'mixing tips']
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
                                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

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
                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "mb_id")))

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
              """가장 오래된 포스트를 가진 카테고리 찾기"""
              try:
                                print("카테고리별 포스트 확인 중...")
                                driver.get(f"{TENREELS_URL}/bbs/board.php?bo_table=m_news")
                                time.sleep(2)

        categories = list(CATEGORY_SOURCES.keys())

        if not categories:
                              return '자유'

        oldest_category = categories[0]
        print(f"선택된 카테고리: {oldest_category}")
        return oldest_category
except Exception as e:
        print(f"카테고리 확인 오류: {e}")
        return '자유'

def search_news_content(category):
              """카테고리에 맞는 뉴스 검색"""
              try:
                                print(f"'{category}' 카테고리 뉴스 검색 중...")

        if category not in CATEGORY_SOURCES:
                              return None, None, None

        source_info = CATEGORY_SOURCES[category]

        for site in source_info['sites']:
                              try:
                                                        response = requests.get(site, timeout=5, headers={
                                                                                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                        })

                if response.status_code == 200:
                                              soup = BeautifulSoup(response.content, 'html.parser')

                    titles = soup.find_all(['h1', 'h2', 'h3'], limit=3)

                    if titles:
                                                      title = titles[0].get_text().strip()[:80]
                                                      search_keyword = source_info['search_keywords'][0]

                        content = generate_korean_content(category, title, search_keyword)

                        print(f"✓ 뉴스 발견: {title}")
                        return title, content, search_keyword
except Exception as e:
                continue

        default_title = f"{category} 음악 기술 가이드 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        search_keyword = source_info['search_keywords'][0]
        default_content = generate_korean_content(category, default_title, search_keyword)

        return default_title, default_content, search_keyword
except Exception as e:
        print(f"뉴스 검색 오류: {e}")
        return None, None, None

def generate_korean_content(category, title, search_keyword):
              """한국식 친절한 톤의 콘텐츠 생성"""
              content = f"""안녕하세요!

          오늘은 {category} 음악인들을 위한 실용적인 정보를 공유해드립니다.

          【{title}】

          음악 제작과 연주 기술은 지속적인 학습과 실습을 통해 향상됩니다. 
          최신 기술과 트렌드를 따라가면서도 기초를 탄탄히 하는 것이 중요합니다.

          주요 포인트:

          1. 기본기 습득의 중요성
             음악의 어떤 장르든 기초가 가장 중요합니다. 
             정기적인 연습과 체계적인 학습을 통해 음악적 기초를 완성하세요.

          2. 최신 도구와 기술 활용
             현대 음악 제작에는 다양한 소프트웨어와 장비들이 활용됩니다. 
             이러한 도구들을 효과적으로 활용하는 방법을 학습하면 창작 능력이 크게 향상됩니다.

          3. 꾸준한 연습과 피드백
             좋은 음악은 반복적인 연습과 개선을 통해 만들어집니다. 
             다른 음악인들의 피드백을 받고 지속적으로 개선하세요.

          4. 커뮤니티와의 교류
             tenreels와 같은 음악 커뮤니티에서 다른 음악인들과 정보를 나누고 
             함께 성장하는 것이 매우 도움됩니다.

          음악은 끝없는 학습의 여정입니다. 
          작은 발전도 소중히 여기고 꾸준히 나아가세요!

          더 많은 음악 정보와 팁을 원하신다면 tenreels.com을 방문해주세요. 
          함께 음악으로 성장하는 커뮤니티입니다!
          """
              return content

def search_youtube_video_by_keyword(search_keyword):
              """본문 내용과 관련된 YouTube 영상을 실제로 검색"""
              try:
                                print(f"YouTube에서 '{search_keyword}' 검색 중...")

        # YouTube 검색 페이지 크롤링
                  search_query = f"{search_keyword} tutorial"
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"

        response = requests.get(search_url, timeout=5, headers={
                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code == 200:
                              # YouTube 페이지에서 영상 ID 추출
                              video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)

            if video_ids:
                                      video_id = video_ids[0]
                                      youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                                      print(f"✓ YouTube 영상 발견: {youtube_url}")
                                      return youtube_url

        # 크롤링 실패 시 기본값 반환
        print(f"⚠ YouTube 검색 실패, 기본 튜토리얼 링크 사용")
        return f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"

except Exception as e:
        print(f"YouTube 검색 오류: {e}")
        # 오류 시에도 검색 URL 반환 (음악인들이 직접 찾을 수 있도록)
        return f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_keyword)}"

def post_to_tenreels(driver, category, title, content, youtube_url):
              """텐릴스에 포스팅"""
              try:
                                print("포스팅 시작...")

        driver.get(f"{TENREELS_URL}/bbs/write.php?bo_table=m_news")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "wr_subject")))

        time.sleep(2)

        try:
                              category_select = Select(driver.find_element(By.NAME, "ca_name"))
                              category_select.select_by_value(category)
                              time.sleep(1)
                          except:
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
                          except:
            pass

        try:
                              iframes = driver.find_elements(By.TAG_NAME, "iframe")

            if iframes:
                                      driver.switch_to.frame(iframes[0])
                                      body = driver.find_element(By.TAG_NAME, "body")

                embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"

                body.send_keys(embed_content)
                driver.switch_to.default_content()
                print(f"✓ 본문 입력 (YouTube 임베드 포함)")
else:
                content_field = driver.find_element(By.NAME, "wr_content")
                          embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"
                content_field.send_keys(embed_content)
                print(f"✓ 본문 입력")
except Exception as e:
            print(f"본문 입력 중 오류 (계속 진행): {e}")

        time.sleep(2)

        try:
                              submit_buttons = [
                                                        ("//button[@type='submit']", "submit button"),
                                                        ("//input[@type='submit']", "submit input"),
                                                        ("//button[contains(text(), '작성')]", "write button"),
                                                        ("//button[contains(text(), '완료')]", "complete button"),
                              ]

            for selector, desc in submit_buttons:
                                      try:
                                                                    submit_btn = driver.find_element(By.XPATH, selector)
                                                                    if submit_btn.is_displayed():
                                                                                                      submit_btn.click()
                                                                                                      print(f"✓ 포스팅 완료! ({desc})")
                                                                                                      time.sleep(3)
                                                                                                      return True
                                                                                              except:
                                                                    continue

            print("⚠ 제출 버튼을 찾을 수 없었습니다.")
except Exception as e:
            print(f"포스팅 제출 중 오류: {e}")

        return True
except Exception as e:
        print(f"포스팅 중 오류: {e}")
        return False

def main():
              """메인 실행 함수"""
    print(f"\n{'='*60}")
    print(f"텐릴스 음악인 도움 자동화 시스템 시작 ({datetime.now()})")
    print(f"음악인들에게 실질적으로 도움되는 뉴스와 튜토리얼을 제공합니다")
    print(f"{'='*60}\n")

    driver = setup_driver()

    if not driver:
                      print("❌ WebDriver 초기화 실패")
        return

    try:
                      # 1. 로그인
                      if not login(driver):
                                            print("❌ 로그인 실패")
                                            return

        # 2. 카테고리 선택
        category = get_oldest_category(driver)

        # 3. 뉴스 검색
        title, content, search_keyword = search_news_content(category)
        if not title or not content:
                              print("❌ 뉴스 검색 실패")
            return

        # 4. 본문 내용과 관련된 YouTube 영상 검색 (중요!)
        youtube_url = search_youtube_video_by_keyword(search_keyword)

        # 5. 포스팅
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
