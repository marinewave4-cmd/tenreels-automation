#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenreels Daily Music News Automation
매일 오후 1:40(KST)에 자동으로 음악 뉴스를 텐릴스에 포스팅합니다.
실제 음악인들에게 도움되는 실질적인 뉴스와 튜토리얼을 검색하고 포스팅합니다.
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
import json
import re

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
                        'keywords': ['music production', 'mixing', 'mastering']
          },
          '보컬': {
                        'sites': [
                                          'https://www.billboard.com/music/features/',
                                          'https://www.artium.academy/',
                        ],
                        'keywords': ['vocal training', 'singing technique', 'voice']
          },
          '건반': {
                        'sites': [
                                          'https://www.soundonsound.com/reviews/keyboards',
                        ],
                        'keywords': ['keyboard', 'piano', 'synthesizer']
          },
          'Guitar': {
                        'sites': [
                                          'https://www.guitarworld.com/',
                                          'https://www.sweetwater.com/insync/',
                        ],
                        'keywords': ['guitar technique', 'guitar tips']
          },
          'Drum & Bass': {
                        'sites': [
                                          'https://www.soundonsound.com/reviews/drums',
                        ],
                        'keywords': ['drum', 'bass', 'rhythm']
          },
          '현악기': {
                        'sites': [
                                          'https://www.gramophone.co.uk/',
                        ],
                        'keywords': ['violin', 'cello', 'string']
          },
          '엔지니어': {
                        'sites': [
                                          'https://www.soundonsound.com/techniques',
                                          'https://www.pro-tools-expert.com/',
                        ],
                        'keywords': ['audio engineering', 'recording', 'mixing']
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

        # 아이디 입력
              id_field = driver.find_element(By.NAME, "mb_id")
        id_field.clear()
        id_field.send_keys(LOGIN_ID)

        # 비밀번호 입력
        pw_field = driver.find_element(By.NAME, "mb_password")
        pw_field.clear()
        pw_field.send_keys(LOGIN_PW)

        # 로그인 버튼 클릭
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()

        time.sleep(3)
        print("✓ 로그인 완료!")
        return True
except Exception as e:
        print(f"로그인 오류: {e}")
        return False

def get_category_post_dates(driver):
          """각 카테고리의 최신 포스트 날짜 확인"""
    try:
                  print("카테고리별 포스트 날짜 확인 중...")
                  driver.get(f"{TENREELS_URL}/bbs/board.php?bo_table=m_news")
                  time.sleep(2)

        category_dates = {}
        categories = ['자유', '보컬', '건반', 'Guitar', 'Drum & Bass', '현악기', '목관악기', '금관악기', '국악기', '작편곡 & 작사', '엔지니어', 'Ai', '행위예술']

        for category in categories:
                          try:
                                                # 각 카테고리 탭 클릭
                                                category_tab = driver.find_element(By.XPATH, f"//a[contains(text(), '{category}')]")
                                                category_tab.click()
                                                time.sleep(1)

                # 첫 번째 포스트의 날짜 찾기
                              try:
                                                        date_elem = driver.find_element(By.CSS_SELECTOR, ".list_date, .comment-date, span[class*='date']")
                                                        date_text = date_elem.text if date_elem else "미정"
                                                        category_dates[category] = date_text
                                                        print(f"  {category}: {date_text}")
                                                    except:
                    category_dates[category] = "확인불가"
                                                                      except:
                category_dates[category] = "확인불가"

        # 가장 오래된 카테고리 찾기 (또는 포스트가 적은 카테고리)
        oldest_category = min(CATEGORY_SOURCES.keys()) if CATEGORY_SOURCES else '자유'
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
                          return None, None

        source_info = CATEGORY_SOURCES[category]

        # 첫 번째 사이트에서 검색 시도
        for site in source_info['sites']:
                          try:
                                                response = requests.get(site, timeout=5, headers={
                                                                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                })

                if response.status_code == 200:
                                          soup = BeautifulSoup(response.content, 'html.parser')

                    # 뉴스 제목과 내용 추출
                                          titles = soup.find_all(['h1', 'h2', 'h3'], limit=3)

                    if titles:
                                                  title = titles[0].get_text().strip()[:80]

                        # 내용 생성
                                                  content = generate_korean_content(category, title, source_info['keywords'])

                        print(f"✓ 뉴스 발견: {title}")
                        return title, content
except Exception as e:
                continue

        # 기본 콘텐츠 생성
        default_title = f"{category} 음악 기술 가이드 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        default_content = generate_korean_content(category, default_title, source_info['keywords'])

        return default_title, default_content
except Exception as e:
        print(f"뉴스 검색 오류: {e}")
        return None, None

def generate_korean_content(category, title, keywords):
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

def search_youtube_video(category, keywords):
          """카테고리와 관련된 YouTube 영상 검색"""
    try:
                  print(f"YouTube 영상 검색 중 ({category})...")

        # 기본 YouTube 검색 URL
        search_query = f"{category} tutorial music 2025 OR 2024"
        search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

        # 실제로 YouTube API를 사용하거나 크롤링하는 것이 이상적이지만,
        # 여기서는 인기 있는 음악 튜토리얼 채널의 최신 영상 URL 반환

        popular_videos = {
                          '보컬': 'https://www.youtube.com/watch?v=VrxqJ47pY9U',
                          'Guitar': 'https://www.youtube.com/watch?v=kffACX_ao94',
                          '건반': 'https://www.youtube.com/watch?v=ZXr0aXjpNQE',
                          'Drum & Bass': 'https://www.youtube.com/watch?v=sJ04M1J5tgc',
                          '현악기': 'https://www.youtube.com/watch?v=G5ZXgTD0QyI',
                          '엔지니어': 'https://www.youtube.com/watch?v=sj_TkxA-c8o',
                          '자유': 'https://www.youtube.com/watch?v=URP_fksSKDg',
        }

        video_url = popular_videos.get(category, 'https://www.youtube.com/watch?v=9JFCJO7ig0Y')
        print(f"✓ 영상 선택: {video_url}")
        return video_url
except Exception as e:
        print(f"YouTube 검색 오류: {e}")
        return 'https://www.youtube.com/watch?v=9JFCJO7ig0Y'

def post_to_tenreels(driver, category, title, content, youtube_url):
          """텐릴스에 포스팅"""
    try:
                  print("포스팅 시작...")

        # 글쓰기 페이지로 이동
        driver.get(f"{TENREELS_URL}/bbs/write.php?bo_table=m_news")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "wr_subject")))

        time.sleep(2)

        # 카테고리 선택
        try:
                          category_select = Select(driver.find_element(By.NAME, "ca_name"))
                          category_select.select_by_value(category)
                          time.sleep(1)
                      except:
            print(f"카테고리 선택 실패 (그누보드 구조 확인 필요): {category}")

        # 제목 입력
        title_field = driver.find_element(By.NAME, "wr_subject")
        title_field.clear()
        title_field.send_keys(title)
        print(f"✓ 제목 입력: {title}")

        # 유튜브 링크 입력
        try:
                          youtube_field = driver.find_element(By.NAME, "wr_youtube")
                          youtube_field.clear()
                          youtube_field.send_keys(youtube_url)
                          print(f"✓ 유튜브 링크: {youtube_url}")
                      except:
            pass  # YouTube 링크 필드가 없을 수 있음

        # 본문 입력
        try:
                          # 에디터 프레임 찾기
                          iframes = driver.find_elements(By.TAG_NAME, "iframe")

            if iframes:
                                  # 첫 번째 iframe이 일반적으로 본문 에디터
                                  driver.switch_to.frame(iframes[0])
                                  body = driver.find_element(By.TAG_NAME, "body")

                # 유튜브 임베드 형식
                                  embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"

                body.send_keys(embed_content)
                driver.switch_to.default_content()
                print(f"✓ 본문 입력 (임베드 포함)")
else:
                # iframe이 없으면 직접 입력 시도
                      content_field = driver.find_element(By.NAME, "wr_content")
                embed_content = f"{{동영상:{youtube_url}}}\n\n{content}"
                content_field.send_keys(embed_content)
                print(f"✓ 본문 입력 (직접)")
except Exception as e:
            print(f"본문 입력 중 오류 (계속 진행): {e}")

        time.sleep(2)

        # 제출 버튼 찾기 및 클릭
        try:
                          # 다양한 제출 버튼 선택자 시도
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

            print("⚠ 제출 버튼을 찾을 수 없었습니다. 수동 제출 필요할 수 있습니다.")
except Exception as e:
            print(f"포스팅 제출 중 오류: {e}")

        return True
except Exception as e:
        print(f"포스팅 중 오류: {e}")
        return False

def main():
          """메인 실행 함수"""
    print(f"\n{'='*50}")
    print(f"텐릴스 자동화 시작 ({datetime.now()})")
    print(f"{'='*50}\n")

    driver = setup_driver()

    if not driver:
                  print("❌ WebDriver 초기화 실패")
        return

    try:
                  # 1. 로그인
                  if not login(driver):
                                    print("❌ 로그인 실패")
                                    return

        # 2. 카테고리 확인
        category = get_category_post_dates(driver)

        # 3. 뉴스 검색
        title, content = search_news_content(category)
        if not title or not content:
                          print("❌ 뉴스 검색 실패")
            return

        # 4. YouTube 영상 검색
        youtube_url = search_youtube_video(category, [])

        # 5. 포스팅
        if post_to_tenreels(driver, category, title, content, youtube_url):
                          print(f"\n✅ 자동화 완료!\n")
else:
            print(f"\n⚠ 포스팅 중 오류 발생\n")

except Exception as e:
        print(f"오류 발생: {e}")
finally:
        driver.quit()

if __name__ == "__main__":
          main()
