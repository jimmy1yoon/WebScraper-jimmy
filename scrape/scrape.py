from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json, os, re, yaml
from command import Commands
from db import DB
from utils import Utils

class Scrape : 
    
    def __init__(self, cmd : Commands, db : DB) -> None:
        self._driver = None
        self._cmd = cmd if cmd is not None else Commands(None)
        self._db = db if db is not None else DB(None)
        self._config = None
        
    @property
    def command(self):
        return self._cmd
    
    @property
    def db(self):
        return self._db
    
    @property
    def driver(self):
        if self._driver is None : self.open_driver()
        return self._driver
    
    @property
    def config(self):
        '''config.yaml의 설정파일 불러오기'''
        if self._config is None : 
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml'), 'r') as f:
                self._config =  yaml.safe_load(f)
        return self._config
        
#-------- create selenium driver
        
    def open_driver(self):
        '''selenium chrome driver 설정 및 생성 후 입력받은 url open'''
        options = webdriver.ChromeOptions() # remove USB로 인식하는 error 제거 options 
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-usb-keyboard-detect")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_argument('--disable-blink-features=AutomationControlled')
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        self._driver = webdriver.Chrome(os.getcwd()+'/chromedriver_win32/chromedriver.exe', options=options, desired_capabilities=caps)
        self.open_page(self.command.url)
        
    def open_page(self, url = None):
        '''url에 맞는 page로 이동 후 0.3 대기'''
        try:
            self.driver.get(url) # 이동
            self.driver.implicitly_wait(0.3) # 로딩
        except WebDriverException as e: # url이 없을 경우 Error
            raise f"Error: Invalid URL" 
    
#-------- Get information with JavaScript
        
    def get_page_url(self) -> list[dict]:
        ''' javascripts querySelectorAll() 함수를 활용하여 a.href, a.outerHTML 추출
        return {'href' : row.href, 'outerHTML' : row.outerHTML}
        '''
        script = '''let elements = Array.from(document.querySelectorAll('a'))
            .filter((content) => content.href.startsWith('https://') && content.host == document.location.host)
            .map((row) => ({'href' : row.href, 'outerHTML' : row.outerHTML}));
        return JSON.stringify(elements);
        ''' 
        results =  self.driver.execute_script(script)
        return json.loads(results)

    def get_url_html(self) -> list[dict]:
        '''javascripts querySelectorAll() 함수를 활용하여 필요한 HTML 요소추출
        ##TODO : get_url과 합체
        
        return {'baseURI': 현재 URL, 'tagName': tag이름, 'className': 클래스명, 'href': tag.href, 'textContent':tag 텍스트 내용 ,'outerHTML' : outerHTML}
        '''
        script = '''let elements = Array.from(document.querySelectorAll('a'))
            .filter((content) => content.host == document.location.host)
            .map((row) => ({'baseURI': row.baseURI, 'tagName':row.tagName, 'className': row.className, 'href': row.href, 'textContent':row.textContent.trim() ,'outerHTML' : row.outerHTML}));
        return JSON.stringify(elements);
        '''
        results =  self.driver.execute_script(script)
        return json.loads(results)
    
    def has_media_tag_script(self, tag_name:str):
        '''html script 내의 광고 매체별 keyword 포함 여부 확인'''
        return f"0<document.querySelectorAll('script[src*={tag_name}]').length"
    
    def has_media_tag(self, **validations)->dict :
        ''' 광고 매체별 태그 설치 여부를 dict 형태로 반환
        return {google : 1, facebook : 1, kakao : 0, naver : 1}
        '''
        return {channel:json.loads(self.driver.execute_script(f'return JSON.stringify({self.has_media_tag_script(tag_name)})')) for channel, tag_name in validations.items()}
    
    def get_url(self):
        url_list = [Utils.change_href(row) for row in self.get_page_url()]
        return url_list
        
#-------- run the command function
    def get_logs(self):
        '''get network log
        
        ##TODO 광고 매체별 request log 추출 / get method 이외에 post request 파라미터 추출
        '''
        logs = self.driver.get_log('performance')
        text = 'collect' # log 중 탐지할 키워드
        for log in logs:
            log_message = json.loads(log['message'])
            if log_message['message']['method'] == 'Network.requestWillBeSent' and text in log_message['message']['params']['request']['url']:
                request_url = log_message['message']['params']['request']
                url, parameter = request_url.split('?')
                print(Utils.parse_parameter(parameter))
                
    def get_html_elements(self):
        visited = []
        tablename = 'html_elements' if self.command.table is None else self.command.table
        for row in self.get_url_html():
            if row not in visited: 
                visited.append(row)
                self.db.insert_row(tablename, tuple(row.keys()), tuple(row.values()))
        
    def get_valid(self, url = None) -> dict:
        '''html scripts를 보며 광고 tag 설치 여부 확인'''
        if url is None:
            url = self.command.url
        table_name = 'tag_valid'
        data = self.has_media_tag(**self.config['MEDIA_TAG'])
        self.db.insert_row(table_name, tuple(data.keys()), tuple(data.values()))
        self.db.insert_row(table_name, ('baseURI',) , (url,))
        
    def get_elem_in_page(self, url) -> None:
        '''페이지의 필요한 정보 수집 함수들을 한번에 실행'''
        self.get_html_elements()
        self.get_valid(url)
        
    def get_main(self):
        visited = []
        self.get_elem_in_page()
        url_list = self.get_url(self.command.url)
        # input("로그인 하셨습니까? (y/n): ") # google login은 안됌
        for i, url in enumerate(url_list):
            print(f'{i / len(url_list) * 100}% 진행 중')
            if url not in visited and i < 30:
                visited.append(url)
                self.open_page(url)
                self.get_elem_in_page()
            else:
                break
        
# ---------- DB ------------
                
    def create(self):
        columns = self.config['create_table'][self.command.table]
        self.db.create_table(self.command.table, **columns)
                
    def select(self):
        columns = ['*'] if self.command.columns is None else self.command.columns
        data = self.db.select_table(self.command.table, columns)
        
    def drop(self):
        self.db.drop_table(self.command.table)