import sqlite3
import re, os

class DB:
    
    def __init__(self, db_name : str) -> None:
        self.make_db(db_name)
        
    @property
    def cur(self):
        return self._cur
    
    @property
    def con(self):
        return self._con
        
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
                
    def commit(self):
        '''DB 변경사항을 commit'''
        self.con.commit()
                
    def drop_table(self, name:str):
        ''' sqlite 'drop table' 실행
        - parameter
            - name : drop할 table 이름
        '''
        query = f'DROP TABLE IF EXISTS {name}'
        self.cur.execute(query)
        self.commit()
                
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
                
    def rename_col(self, table_name:str, name_current:str, name_new):
        ''' sqlite rename column 실행
        - parameter
            - table_name : 변경할 columns이 속해있는 table name
            - 
        '''
        query = f'ALTER TABLE {table_name} RENAME COLUMN {name_current} TO {name_new};'
        self.cur.execute(query)
        self.commit()
                
    def insert_row(self, name, columns:tuple, items:tuple):
        ''' sqlite insert 명령문 실행
        - parameter
            - name : table name
            - columns : columns name (tuple)
            - items : values
            '''
        col_str = ''
        for item in columns:
            col_str = col_str + '?,'
        if len(columns) == 1:
            columns = str(columns).replace(',', '')
        query = f"INSERT INTO {name} {columns} VALUES ({col_str.rstrip(',')});"
        self.cur.execute(query,items)
        self.commit()
        
    def delete_table(self, name):
        '''sqlite delete 명령문 실행
        - parameter
            - name : table name
        '''
        self.cur.execute(f'DELETE FROM {name}')
        self.commit()
        
    def select_table(self, name:str, columns:list):
        '''sqlite select 명령문 실행
        - parameter
            - name : table name
            - columns : columns
        '''
        columns = str(columns).strip('[]')
        query = f"SELECT {columns} FROM {name};"
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data