import sqlite3
import re, os

class DB:
    
    def __init__(self, db_name : str, config: dict) -> None:
        self.make_db(db_name)
        self._config = config
        
    @property
    def cur(self):
        return self._cur
    
    @property
    def con(self):
        return self._con
    
    @property
    def config(self):
        return self._config
        
    def make_db(self, db_name) -> None:
        '''db가 있을 경우 connect 없을 경우 새로운 .db 파일 생성'''
        filename = f'{db_name}.db'
        db_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+f'\db\{filename}'
        if not os.path.exists(db_path):
            make_file = input('새로운 DB를 만드시겠습니까? (y/n)')
            if make_file != 'y' or make_file != 'Y':
                raise('DB 연결 오류')
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()
    
    def check_table(self, table_name:str):
        '''insert 전 table 존재 유무 확인
        
        table이 없을 경우 create table 실행
        - parameter
            - table_name : check 할 table name
        '''
        query = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self.cur.execute(query)
        if self.cur.fetchone()[0] == 0:
            columns = self.config['create_table'][table_name]
            self.create_table(table_name, **columns)
            
    def rename_col(self, table_name:str, name_current:str, name_new):
        ''' sqlite rename column 실행
        - parameter
            - table_name : 변경할 columns이 속해있는 table name
            - 
        '''
        query = f'ALTER TABLE {table_name} RENAME COLUMN {name_current} TO {name_new};'
        self.cur.execute(query)
        self.con.commit()
                
    def insert_row(self, table_name, columns:tuple, items:tuple):
        ''' sqlite insert 명령문 실행
        - parameter
            - name : table name
            - columns : columns name (tuple)
            - items : values
            
        ##TODO : 중복 Check -> 현재는 중복 check 없이 모든 row를 insert 
        '''
        self.check_table(table_name)
        col_str = ''
        for item in columns:
            col_str = col_str + '?,'
        if len(columns) == 1:
            columns = str(columns).replace(',', '')
        query = f"INSERT INTO {table_name} {columns} VALUES ({col_str.rstrip(',')});"
        self.cur.execute(query,items)
        self.con.commit()
        
                    
    def create_table(self, name:str, **columns):
        ''' sqlite 'create table' 실행
        - parameter
            - index를 추가한다면 columns의 첫번째로 '''
        col_str = ''
        for col_name, col_type in columns.items():
            col_str = col_str + f'{col_name} {col_type},'
        col_str = col_str.rstrip(',')
        query = f'CREATE TABLE {name} ({col_str})'
        self.cur.execute(query)     
                    
    def drop_table(self, name:str):
        ''' sqlite 'drop table' 실행
        - parameter
            - name : drop할 table 이름
        '''
        query = f'DROP TABLE IF EXISTS {name}'
        self.cur.execute(query)
        self.con.commit()   
        
    def delete_table(self, table_name):
        '''sqlite delete 명령문 실행
        - parameter
            - name : table name
        '''
        self.cur.execute(f'DELETE FROM {table_name}')
        self.con.commit()
        
    def select_table(self, table_name:str, columns:list):
        '''sqlite select 명령문 실행
        - parameter
            - name : table name
            - columns : columns
        '''
        columns = str(columns).strip('[]')
        query = f"SELECT {columns} FROM {table_name};"
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data