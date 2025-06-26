import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

def crawl_hi_faq():
    url = "https://www.hi.co.kr/serviceAction.do?menuId=101210"

    options = Options()
    # options.add_argument("--headless")  # 필요 시 사용
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(2)

    results = []
    seen_questions = set()

    def extract_current_page_questions():
        a_tags = driver.find_elements(By.CSS_SELECTOR, "a[href^='#panel-']")
        for a in a_tags:
            try:
                subject = a.find_element(By.CSS_SELECTOR, "span.mark").text.strip()
                question = a.find_element(By.CSS_SELECTOR, "p").text.strip()

                if question in seen_questions:
                    continue
                seen_questions.add(question)

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", a)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", a)
                time.sleep(0.5)

                try:
                    active_panel = driver.find_element(By.CSS_SELECTOR, "div.panel.active")
                    p_tags = active_panel.find_elements(By.TAG_NAME, "p")
                    content = "\n".join([p.text.strip() for p in p_tags if p.text.strip()])
                except NoSuchElementException:
                    content = ""

                results.append({
                    "subject": subject,
                    "question": question,
                    "content": content
                })

            except Exception as e:
                print(f"[질문 처리 중 오류] {e}")
                continue

    # 반복: 질문 수집 후 더보기 버튼 클릭
    while True:
        extract_current_page_questions()

        try:
            btn = driver.find_element(By.CLASS_NAME, "btn_more")
            if btn.is_displayed() and btn.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)  # 새 항목 로딩 대기
            else:
                break
        except NoSuchElementException:
            break  # 더 이상 버튼이 없을 때 종료
        except ElementClickInterceptedException:
            print("[경고] 버튼 클릭 실패 - 무시하고 종료")
            break

    driver.quit()

    with open("hi_faq_final.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"총 {len(results)}개의 항목 저장 완료")

if __name__ == "__main__":
    crawl_hi_faq()
