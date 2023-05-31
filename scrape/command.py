import argparse, re, sys

class Commands():
    
    _KEY_PARSER_URL = 'url'
    _KEY_PARSER_ID = 'id'
    _KEY_PARSER_PASSWORD = 'password'
    _KEY_PARSER_SQL = 'sql'
    _KEY_PARSER_DB = 'db'
    
    @property
    def url(self) -> str:
        return self._url
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def password(self) -> str:
        return self._password
    
    @property
    def table(self) -> str:
        return self._table
    
    @property
    def columns(self) -> str:
        return self._columns
    
    @property
    def func(self) -> str:
        return self._function
    
    @property
    def db(self) -> str:
        return self._db

    def __init__(self, *args):
        self._parser = self._build_parser()
        self.load(args)
    
    def _build_parser(self):
        '''command 입력을 위한 argument parser 설정'''
        parser = argparse.ArgumentParser(prog= 'crawling', description='crawling tags in website')
        parser.add_argument('--url', type=str, required=True ,help='input url')
        parser.add_argument('--id', type=str,help='input id')
        parser.add_argument('--password', type=str, help='input password')
        parser.add_argument('--db', type=str, required=True, help='db name')
        parser.add_argument('--sql', type=str, help='sql query ex) tablename[columns]') 
        parser.add_argument('--func', type=str, required=True, help='run function')
        return parser
    
    def load(self,args = sys.argv):
        '''parser 결과를 저장'''
        self._items = vars(self._parser.parse_args(*args))
        self._url = self.add_https(self._items['url'])
        self._id = self._items[self._KEY_PARSER_ID]
        self._password = self._items[self._KEY_PARSER_PASSWORD]
        self.parse_sql(self._items[self._KEY_PARSER_SQL])
        self._db = self._items[self._KEY_PARSER_DB]
        self._function = self._items['func']
        
    def add_https(self, url):
        '''입력받은 url이 https 로 시작하지 않는 경우 https:// 추가'''
        if not url.startswith("https"):
            url = "https://" + url
        return url
        
    def parse_sql(self, query):
        ''' "sql" 명령어 parse 
        
        입력방식: 'TABLE NAME[col1, col2, col3]' 필요시 [col name..] 은 생략 가능
        '''
        if query is None:
            self._table = None
            self._columns = None
        else:
            self._table = re.match(r'\w+', query).group()
            column_list = re.findall(r'\w+', query[len(self._table):])
            if not column_list:
                column_list = None
            self._columns = column_list