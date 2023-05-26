import sqlite3
import re

class DB:
    
    def __init__(self, urlname : str) -> None:
        self.make_db(urlname)
        
    @property
    def cur(self):
        return self._cur
    
    @property
    def con(self):
        return self._con
        
    def make_db(self, url) -> None:
        filename = 'galaxycampus.db'
        try:
            self._con = sqlite3.connect(f'./crawling/{filename}')
            self._cur = self._con.cursor()

        except FileNotFoundError:
            pass
                
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
        col_cnt = ''
        for item in columns:
            col_cnt = col_cnt + '?,'
        query = f"INSERT INTO {name} {columns} VALUES ({col_cnt.rstrip(',')});"
        self.cur.execute(query,items)
        self.commit()
        
    def delete_table(self, name):
        self.cur.execute(f'DELETE FROM {name}')
        self.commit()
        
    def select_table(self, name):
        query = f"SELECT * FROM {name};"
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data