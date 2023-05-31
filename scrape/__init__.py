from scrape import Scrape
from command import Commands
from db import DB
import os, yaml


def main(args) :
    # load command
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml'), 'r') as f:
        config =  yaml.safe_load(f)

    # bulid_parser
    cmd = Commands(args) # command 명령어로 Command 인스턴스 생성
    # runner
    db = DB(cmd.db, config) # command.db 이름을 통해 DB 인스턴스 생성
    crl = Scrape(cmd, db) # Scrape 인스턴스 생성시 Command, DB 인스턴스를 함께 전달

    try:
        func = getattr(crl, cmd.func) #command.func 이름과 동일한 Scrape 함수 
    except AttributeError:
        raise 'AttributeError occurred : invalid function name'
    
    func() #함수 실행