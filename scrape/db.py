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
        filename = f'{db_name}.db'
        db_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+f'\db\{filename}'
        if not os.path.exists(db_path):
            make_file = input('새로운 DB를 만드시겠습니까? (y/n)')
            if make_file != 'y' or make_file != 'Y':
                raise('DB 연결 오류')
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()
                
    def commit(self):
        self.con.commit()
                
    def drop_table(self, name):
        query = f'DROP TABLE IF EXISTS {name}'
        self.cur.execute(query)
        self.commit()
                
    def create_table(self, name:str, **columns):
        '''index를 추가한다면 columns의 첫번째로 '''
        col_str = ''
        for col_name, col_type in columns.items():
            col_str = col_str + f'{col_name} {col_type},'
        col_str = col_str.rstrip(',')
        query = f'CREATE TABLE {name} ({col_str})'
        self.cur.execute(query)        
                
    def rename_col(self, table_name:str, name_current:str, name_new):
        query = f'ALTER TABLE {table_name} RENAME COLUMN {name_current} TO {name_new};'
        self.cur.execute(query)
        self.commit()
                
    def insert_row(self, name, columns:tuple, items:tuple):
        col_str = ''
        for item in columns:
            col_str = col_str + '?,'
        query = f"INSERT INTO {name} {columns} VALUES ({col_str.rstrip(',')});"
        self.cur.execute(query,items)
        self.commit()
        
    def delete_table(self, name):
        self.cur.execute(f'DELETE FROM {name}')
        self.commit()
        
    def select_table(self, name:str, columns:list):
        columns = str(columns).strip('[]')
        query = f"SELECT {columns} FROM {name};"
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data