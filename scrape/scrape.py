from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json, os, re, yaml
from command import Commands
from db import DB

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
        
    def open_driver(self):
        options = webdriver.ChromeOptions() # remove USB로 인식하는 error 제거 options 
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--disable-usb-keyboard-detect")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        self._driver = webdriver.Chrome(os.getcwd()+'/chromedriver_win32/chromedriver.exe', options=options, desired_capabilities=caps)
        self.open_page(self.command.url)
        
    def open_page(self, url = None):
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(0.3)
        except WebDriverException as e:
            raise f"Error: Invalid URL"
        
    def get_page_url(self) -> list[str]:
        script = '''let elements = Array.from(document.querySelectorAll('a'))
            .filter((content) => content.href.startsWith('https://') && content.host == document.location.host)
            .map((row) => ({'href' : row.href, 'outerHTML' : row.outerHTML}));
        return JSON.stringify(elements);
        '''
        results =  self.driver.execute_script(script)
        return json.loads(results)
            
    def get_url_html(self) -> list[str]:
        script = '''let elements = Array.from(document.querySelectorAll('a'))
            .filter((content) => content.host == document.location.host)
            .map((row) => ({'baseURI': row.baseURI, 'tagName':row.tagName, 'className': row.className, 'href': row.href, 'textContent':row.textContent.trim() ,'outerHTML' : row.outerHTML}));
        return JSON.stringify(elements);
        '''
        results =  self.driver.execute_script(script)
        return json.loads(results)
    
    def get_html(self) -> list[str]:
        script = '''let elements = Array.from(document.getElementsByTagName('script'))
            .map((scr)=>scr.outerHTML)
            .filter((content)=> content.includes('gtag'));
        return JSON.stringify(elements);
        '''
        return json.loads(self.driver.execute_script(script))
    
    def has_media_tag_script(self, tag_name:str):
        return f"0<document.querySelectorAll('script[src*={tag_name}]').length"
    
    def has_media_tag(self, **validations) :
        return {channel:json.loads(self.driver.execute_script(f'return JSON.stringify({self.has_media_tag_script(tag_name)})')) for channel, tag_name in validations.items()}
    
    def get_valid(self):
        data = self.has_media_tag(**self.config['MEDIA_TAG'])
        self.db.insert_row(self.command.table, tuple(data.keys()), tuple(data.values()))
    
    def get_url(self):
        url_list = [self.change_href(row) for row in self.get_page_url()]
        return url_list
        
    def change_href(self, row):
        regex = r'href\s*=\s*[\'"]#\s*[\'"].*?location\.href\s*=\s*[\'"](.*?)[\'"]'
        match = re.search(regex, row['outerHTML'])
        if match and match.group(1) is not None:
            url = 'https://www.samsungebiz.com' + match.group(1) ## 
        else:
            url = row['href']
        return url
        
    def parse_parameter(self, url:str):
        param_dict = {}
        while url and '&' in url:
            text, url = url.split('&', maxsplit = 1)
            name, parameter = text.split('=')
            param_dict[name] = parameter
        return param_dict
        
    def get_logs(self):
        '''get network log'''
        logs = self.driver.get_log('performance')
        text = 'collect' # log 중 탐지할 키워드
        for log in logs:
            log_message = json.loads(log['message'])
            if log_message['message']['method'] == 'Network.requestWillBeSent' and text in log_message['message']['params']['request']['url']:
                request_url = log_message['message']['params']['request']
                url, parameter = request_url.split('?')
                print(self.parse_parameter(parameter))
                
    def get_html_elements(self):
        visited = []
        for row in self.get_url_html():
            if row not in visited: 
                visited.append(row)
                self.db.insert_row(self.command.table, tuple(row.keys()), tuple(row.values()))
        
    def get_main(self):
        visited = []
        self.get_html_elements()
        url_list = self.get_url()
        input("로그인 하셨습니까? (y/n): ") # google login은 안됌
        for i, url in enumerate(url_list):
            print(f'{i / len(url_list) * 100}% 진행 중')
            if url not in visited and i < 10:
                visited.append(url)
                self.open_page(url)
                self.get_html_elements()
                self.get_valid()
            else:
                break
        
    def test(self):
        print(self.config['MEDIA_TAG'])
                
# ---------- DB ------------
                
    def create(self):
        columns = self.config[f'{self.command.table}_col']
        self.db.create_table(self.command.table, **columns)
                
    def select(self):
        columns = ['*'] if self.command.columns is None else self.command.columns
        data = self.db.select_table(self.command.table, columns)