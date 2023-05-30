# webscraper-jimmy
Web scraper to scrape html, ad tags etc. 

## requirements
---
python 3.5+
  - yaml
  - selenium
  - chrome webdriver
  - sqlite3

## 프로젝트 소개

## 소개

webscraper는 홈페이지내의 광고 태그, HTML 요소와 같은 정보를 페이지를 순환하며 수집하고 저장

## 구현 목표

1. 스노우볼 탐색으로 모든 페이지 탐색

2. 페이지내에 광고 매체별 이벤트 파라미터 수집

**실행 순서**

0. 저장할 DB 입력 -> 없을경우 sqlite db 생성

1. 입력받은 메인 페이지에서 `<a href>` 를 확인하여 이동 가능한 모든 url 수집 

2. 페이지를 돌며 필요한 정보 수집 후 DB에 저장
   1. 페이지내에 필요한 정보(HTML tag)수집 -> insert `html_elements` table
   2. 페이지내에 광고 tag 설치 여부 수집 -> insert `tag_valid` table
   3. 페이지내의 network log 수집 후 원하는 request 수집 **##TODO** 
  
3. 다음 url 로 이동 -> 2 단계 반복
## 실행 방식
### 실행 command 파라미터
- url (***required***) : 탐색할 메인 URL, 탐색 트리의 가장 위의 노드 Ex) --url "https://www.samsung.com/sec/"
- db (***required***) : 수집한 데이터를 저장하거나 추출할 때 사용할 DB 이름 Ex) --db "samsung" 
- sql : sql query문 작성시 Table 과 columns / 입력 형식 --sql "table[col1,col2,col3]"
- func (***required***) : scrape.py 내에서 실행할 def 입력
- ~~id : 로그인시 사용할 id (사용 X)~~
- ~~password : 로그인시 사용할 password (사용 X)~~

**입력 예시**

`python -m scrape --url "탐색할 main url" [--db "연결할 DB 이름"] [--sql "table_name[col1, col2, col3]"] --func "함수이름"`

## 실행 함수
`--func get_main` : 이동가능한 모든 페이지를 이동하며 필요한 모든 정보를 수집하여 DB에 저장

`--func get_valid` : 현재 페이지의 광고 태그 설치 여부를 DB에 저장

`--func get_html_elements` : 현재 페이지의 특정 HTML요소를 DB에 저장

`--func get_log` : 현재 페이지의 log 정보를 수집 (현재 개발 중)

### scrape Class

프로젝트의 main 함수, selenium driver를 활용하여 이동하거나 정보 수집하는 class

**함수 실행 순서**

- `get_url()`
  설명: 페이지 내의 html a.href를 수집하여 이동 가능한 URL을 전부 수집
  1. `get_page_url()` : 현재 페이지내의 a.href, a.outerHTML 두 가지 요소를 수집
  2. `change_href()` : **##TODO** 수집한 href url 중에서 이동 불가능한 url(script 로 이동하는 요소)을 outerHTML코드를 parsing하여 url 업데이트

- `get_html_elements()` 
  설명: 페이지 내의 html a tag 를 수집하여 db에 저장 
  1. `get_url_html()` : 현재 페이지내의 html 요소 수집
  2. html 요소를 html_element table 에 저장
   
  **##TODO** a 태그 이외에 다른 원하는 tag(Ex: button)를 입력받아 함께 저장 

- `get_valid()`
  1. `has_media_tag()` : html script를 통해 현재 페이지 내의 광고 매체별 tag 설치 여부 확인
  2. 설치 여부를 tag_valid 에 저장 

- `get_logs()`
  1. selenium get_log 함수를 통해 log 정보 수집
  2. 그중 원하는 키워드가 들어있는 log 정보만 추출
  3. 원하신 request log 를 추출 후 Utils.parse_parameter()로 parse
  4. **##TODO** 광고 매체별 request log 추출 / get method 이외에 post request 파라미터 추출

- `get_main()`
  1. `get_url()` : web 안의 이동 가능한 url 목록 수집
  2. `get_elem_in_page()` : web내의 정보 수집
  3. 다음 url로 이동하며 2 단계 반복 --> url을 visit에 추가하여 중복된 url은 이동 X

### db Class

SQLite를 사용하여 DB와 상호작용하는 class Ex) select, create, insert 명령문 실행

- `make_db` : init을 통해서 인스턴스가 만들어지면 .db파일을 생성하거나 connect 

- 함수로 구현한 sql 명령어
  - `drop`
  - `create`
  - `rename`
  - `insert`
  - `delete`
  - `select`

### Utils Class

여러 클래스에서 사용되는 static method를 모아놓은 기능 모듈 

### Command Class

입력받은 command 명령어를 parse 하여 scrape 인스턴스에 전달

