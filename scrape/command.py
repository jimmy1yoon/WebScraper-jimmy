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
        parser = argparse.ArgumentParser(prog= 'crawling', description='crawling tags in website')
        parser.add_argument('--url', type=str, required=True ,help='input url')
        parser.add_argument('--id', type=str,help='input id')
        parser.add_argument('--password', type=str, help='input password')
        parser.add_argument('--db', type=str, help='db name')
        parser.add_argument('--sql', type=str, help='sql query ex) tablename[columns]') 
        parser.add_argument('--func', type=str, required=True, help='run function')
        return parser
    
    def load(self,args = sys.argv):
        self._items = vars(self._parser.parse_args(*args))
        self._url = self.add_https(self._items['url'])
        self._id = self._items[self._KEY_PARSER_ID]
        self._password = self._items[self._KEY_PARSER_PASSWORD]
        self._table, self._columns = self.parse_sql(self._items[self._KEY_PARSER_SQL])
        self._db = self._items[self._KEY_PARSER_DB]
        self._function = self._items['func']
        
    def add_https(self, url):
        if not url.startswith("https"):
            url = "https://" + url
        return url
        
    def parse_sql(self, query):
        table_name = re.match(r'\w+', query).group()
        column_list = re.findall(r'\w+', query[len(table_name):])
        if not column_list:
            column_list = None
        return table_name, column_list