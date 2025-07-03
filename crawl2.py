import os
import time
import shutil
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class HyundaiInsuranceDownloader:
    def __init__(self, base_url="https://www.hi.co.kr/serviceAction.do?menuId=100932"):
        self.base_url = base_url
        self.base_download_dir = os.path.join(os.getcwd(), "현대해상_약관")
        self.temp_download_dir = os.path.join(os.getcwd(), "temp_downloads")
        self.downloaded_products = set()  # 이미 다운로드한 상품 추적
        self.setup_browser()
        
    def setup_browser(self):
        """셀레니움 브라우저 설정"""
        chrome_options = Options()
        # 임시 다운로드 디렉토리 생성
        if not os.path.exists(self.temp_download_dir):
            os.makedirs(self.temp_download_dir)
            
        # PDF 자동 다운로드 설정
        prefs = {
            "download.default_directory": self.temp_download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 크롬 드라이버 설정
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def create_directory(self, path):
        """디렉토리 생성"""
        if not os.path.exists(path):
            os.makedirs(path)
            
    def wait_for_element(self, by, selector, timeout=10):
        """요소가 로드될 때까지 대기"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    
    def click_element(self, element):
        """요소 클릭 및 로딩 대기"""
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(1)  # 클릭 후 페이지 로딩 대기
        
    def get_button_text(self, button):
        """버튼에서 텍스트 추출"""
        span = button.find_element(By.TAG_NAME, "span")
        return span.text.strip()
    
    def wait_for_download_and_move(self, target_dir, new_filename):
        """다운로드 완료 대기 및 파일 이동"""
        max_wait_time = 15  # 최대 대기 시간 (초)
        wait_time = 0
        
        # 다운로드 완료 대기
        while wait_time < max_wait_time:
            # .crdownload 또는 .tmp 확장자 파일이 있는지 확인 (다운로드 중)
            downloading_files = glob.glob(os.path.join(self.temp_download_dir, "*.crdownload")) + \
                               glob.glob(os.path.join(self.temp_download_dir, "*.tmp"))
            
            if not downloading_files:
                # 다운로드 중인 파일이 없으면 완료된 것으로 간주
                break
                
            time.sleep(1)
            wait_time += 1
            
        # 가장 최근 다운로드 파일 찾기
        files = [os.path.join(self.temp_download_dir, f) for f in os.listdir(self.temp_download_dir) 
                if os.path.isfile(os.path.join(self.temp_download_dir, f))]
        
        if not files:
            print(f"다운로드된 파일이 없습니다.")
            return False
            
        latest_file = max(files, key=os.path.getctime)
        file_ext = os.path.splitext(latest_file)[1]
        
        # 대상 디렉토리 확인 및 생성
        self.create_directory(target_dir)
        
        # 새 파일 경로 설정
        new_file_path = os.path.join(target_dir, f"{new_filename}{file_ext}")
        
        # 이미 같은 이름의 파일이 있으면 삭제
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
            
        try:
            # 파일 이동
            shutil.move(latest_file, new_file_path)
            print(f"파일 이동 완료: {os.path.basename(latest_file)} -> {os.path.basename(new_file_path)}")
            return True
        except Exception as e:
            print(f"파일 이동 실패: {e}")
            return False
    
    def is_product_downloaded(self, product_name):
        """이미 다운로드한 상품인지 확인"""
        return product_name in self.downloaded_products
    
    def mark_as_downloaded(self, product_name):
        """상품을 다운로드 완료로 표시"""
        self.downloaded_products.add(product_name)
    
    def download_pdfs(self):
        """웹사이트 탐색 및 PDF 다운로드"""
        try:
            # 기본 다운로드 디렉토리 생성
            self.create_directory(self.base_download_dir)
            
            # 웹페이지 열기
            self.driver.get(self.base_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 판매 중 상품 버튼 (lv1)
            lv1_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.lv1")
            for lv1_button in lv1_buttons:
                lv1_text = self.get_button_text(lv1_button)
                print(f"\n[LV1] {lv1_text} 선택")
                self.click_element(lv1_button)
                
                # 보험종류 버튼 (lv2)
                lv2_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.lv2")
                for lv2_button in lv2_buttons:
                    lv2_text = self.get_button_text(lv2_button)
                    print(f"\n[LV2] {lv2_text} 선택")
                    self.click_element(lv2_button)
                    
                    # lv2 폴더 생성
                    lv2_dir = os.path.join(self.base_download_dir, lv2_text)
                    self.create_directory(lv2_dir)
                    
                    # 보험유형 버튼 (lv3)
                    lv3_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.lv3")
                    for lv3_button in lv3_buttons:
                        lv3_text = self.get_button_text(lv3_button)
                        print(f"\n[LV3] {lv3_text} 선택")
                        self.click_element(lv3_button)
                        
                        # lv3 폴더 생성
                        lv3_dir = os.path.join(lv2_dir, lv3_text)
                        self.create_directory(lv3_dir)
                        
                        # 상품명 버튼 (lv4)
                        lv4_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.lv4")
                        for lv4_button in lv4_buttons:
                            lv4_text = self.get_button_text(lv4_button)
                            
                            # 이미 다운로드한 상품이면 건너뛰기
                            if self.is_product_downloaded(lv4_text):
                                print(f"[SKIP] {lv4_text} - 이미 다운로드됨")
                                continue
                                
                            print(f"[LV4] {lv4_text} 선택")
                            self.click_element(lv4_button)
                            
                            # 약관 링크 찾기 및 클릭
                            try:
                                # 테이블 행 찾기
                                rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
                                for row in rows:
                                    # 상품명이 포함된 행 찾기
                                    td_elements = row.find_elements(By.TAG_NAME, "td")
                                    if td_elements and lv4_text in td_elements[0].text:
                                        # 약관 PDF 링크 찾기 (5번째 td의 a 태그)
                                        pdf_links = row.find_elements(By.CSS_SELECTOR, "td:nth-child(5) a.file.pdf")
                                        if pdf_links:
                                            print(f"약관 PDF 다운로드 중: {lv4_text}")
                                            # PDF 링크 클릭
                                            self.click_element(pdf_links[0])
                                            
                                            # 다운로드 완료 대기 및 파일 이동
                                            if self.wait_for_download_and_move(lv3_dir, lv4_text):
                                                # 다운로드 완료 표시
                                                self.mark_as_downloaded(lv4_text)
                                                print(f"[SUCCESS] {lv4_text} 약관 다운로드 완료")
                                            break  # 해당 상품의 첫 번째 약관만 다운로드
                                        else:
                                            print(f"약관 PDF 링크를 찾을 수 없습니다: {lv4_text}")
                            except Exception as e:
                                print(f"약관 다운로드 중 오류 발생: {e}")
        
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
        
        finally:
            # 브라우저 종료
            self.driver.quit()
            
            # 임시 디렉토리 정리
            try:
                shutil.rmtree(self.temp_download_dir)
            except:
                print("임시 디렉토리 삭제 실패")
                
            print("\n모든 약관 다운로드 완료!")
            print(f"총 다운로드한 상품 수: {len(self.downloaded_products)}")

if __name__ == "__main__":
    downloader = HyundaiInsuranceDownloader()
    downloader.download_pdfs()
