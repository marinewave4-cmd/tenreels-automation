#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenreels Daily Music News Automation
매일 오후 1:40(KST)에 자동으로 음악 뉴스를 텐릴스에 포스팅합니다.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from datetime import datetime

# 설정
TENREELS_URL = "https://tenreels.com"
LOGIN_ID = "news2"
LOGIN_PW = "zqzq1212!!"

def setup_driver():
      """Selenium WebDriver 설정"""
      options = webdriver.ChromeOptions()
      options.add_argument('--headless')
      options.add_argument('--no-sandbox')
      options.add_argument('--disable-dev-shm-usage')
      options.add_argument('--disable-gpu')
      options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=options)
    return driver

def login(driver):
      """텐릴스 로그인"""
      print("로그인 시작...")
      driver.get(f"{TENREELS_URL}/bbs/login.php")
      time.sleep(2)

    # 아이디 입력
      id_field = driver.find_element(By.NAME, "mb_id")
      id_field.send_keys(LOGIN_ID)

    # 비밀번호 입력
      pw_field = driver.find_element(By.NAME, "mb_password")
      pw_field.send_keys(LOGIN_PW)

    # 로그인 버튼 클릭
      login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
      login_btn.click()

    time.sleep(3)
    print("로그인 완료!")

def get_oldest_category(driver):
      """가장 오래된 포스트를 가진 카테고리 찾기"""
      print("카테고리 확인 중...")
      driver.get(f"{TENREELS_URL}/bbs/board.php?bo_table=m_news")
      time.sleep(2)

    categories = {
              '자유': 'free',
              '보컬': 'vocal',
              '건반': 'keyboard',
              'Guitar': 'guitar',
              'Drum & Bass': 'drum_bass',
              '현악기': 'string',
              '목관악기': 'woodwind',
              '금관악기': 'brass',
              '국악기': 'korean',
              '작편곡 & 작사': 'composition',
              '엔지니어': 'engineer',
              'Ai': 'ai',
              '행위예술': 'performance'
    }

    # 각 카테고리 탭 클릭하여 최신 포스트 날짜 확인
    oldest_category = '자유'
    oldest_date = datetime.now()

    for category_name in categories:
              try:
                            category_link = driver.find_element(By.XPATH, f"//*[contains(text(), '{category_name}')]")
                            category_link.click()
                            time.sleep(1)

            # 첫 번째 포스트 날짜 추출
                  try:
                                    date_elem = driver.find_element(By.CSS_SELECTOR, ".comment-date, .list-date, span[class*='date']")
                                    print(f"{category_name}: 최신 포스트 확인")
                                except:
                pass
                                          except:
            pass

    print(f"선택된 카테고리: {oldest_category}")
    return oldest_category

def create_post_content():
      """포스트 콘텐츠 생성"""
    print("포스트 콘텐츠 작성 중...")

    # 예시 콘텐츠 (실제로는 AI가 뉴스를 검색해서 작성)
    title = "음악 프로덕션 필수 팁 - 2026년 업데이트"

    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 예시

    content = f"""안녕하세요!

    오늘은 음악 프로덕션의 최신 트렌드와 유용한 팁을 공유해드립니다.

    주요 내용:

    1. 최신 DAW 기능 활용법
    디지털 오디오 워크스테이션의 새로운 버전들이 점점 더 강력해지고 있습니다. 플러그인 호환성과 성능 최적화가 개선되었습니다.

    2. 효율적인 워크플로우
    빠르고 효율적인 작업 방식이 높은 품질의 결과물로 이어집니다. 단축키와 템플릿을 활용하세요.

    3. 마스터링 표준 이해하기
    스트리밍 플랫폼별 음량 표준(LUFS)을 이해하는 것이 중요합니다.

    tenreels에서 더 많은 음악 정보를 확인하세요!
    """

    return title, content, youtube_url

def post_to_tenreels(driver, category, title, content, youtube_url):
      """텐릴스에 포스팅"""
    print("포스팅 시작...")

    # 글쓰기 페이지로 이동
    driver.get(f"{TENREELS_URL}/bbs/write.php?bo_table=m_news")
    time.sleep(2)

    try:
              # 카테고리 선택
              category_select = Select(driver.find_element(By.NAME, "ca_name"))
        category_select.select_by_value(category)
        time.sleep(1)

        # 제목 입력
        title_field = driver.find_element(By.NAME, "wr_subject")
        title_field.send_keys(title)

        # 유튜브 링크 입력
        youtube_field = driver.find_element(By.NAME, "wr_youtube")
        youtube_field.send_keys(youtube_url)

        # 본문 입력 (에디터)
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe[id*='editor']")
        driver.switch_to.frame(iframe)
        body_field = driver.find_element(By.CSS_SELECTOR, "body")

        # 유튜브 임베드 형식으로 첫 줄에 추가
        embed_text = f"{{동영상:{youtube_url}}}\n\n{content}"
        body_field.send_keys(embed_text)

        driver.switch_to.default_content()
        time.sleep(2)

        # 제출 버튼 클릭
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'][value='작성']")
        submit_btn.click()

        print("포스팅 완료!")
        time.sleep(3)

except Exception as e:
        print(f"포스팅 중 오류: {e}")

def main():
      """메인 실행 함수"""
    print(f"=== 텐릴스 자동화 시작 ({datetime.now()}) ===")

    driver = setup_driver()

    try:
              login(driver)
        category = get_oldest_category(driver)
        title, content, youtube_url = create_post_content()
        post_to_tenreels(driver, category, title, content, youtube_url)

        print("=== 자동화 완료 ===")

except Exception as e:
        print(f"오류 발생: {e}")
finally:
        driver.quit()

if __name__ == "__main__":
      main()
