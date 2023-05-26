# webscraper-jimmy
Web scraper to scrape html, ad tags etc. 

## 프로젝트 소개

### 소개

webscraper는 홈페이지내의 광고 태그, HTML 요소와 같은 정보를 페이지를 순환하며 수집하고 저장

### 구현 목표

1. 스노우볼 탐색으로 모든 페이지 탐색

2. 페이지내에 광고 이벤트 파라미터 수집

**실행 순서**

0. 저장할 DB 입력 -> 없을경우 sqlite db 생성

1. 입력받은 메인 페이지에서 `<a href>` 를 확인하여 이동 가능한 모든 url 수집 

2. 페이지내에 필요한 정보(HTML tag)수집 -> insert `html_elements` table

3. 페이지내에 광고 이벤트 파라미터 수집 -> insert `tag_valid` table

4. 다음 url 로 이동 -> 2 ~ 4 단계 반복
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

## 사용 가능 함수
### scrape Class
- `get_html_elements()`
  1. get_url_html() : 현재 페이지내의 html 요소 수집
  2. html 요소를 html_element table 에 저장

- `get_valid()`
  1. self.has_media_tag() : html script를 통해 현재 페이지 내의 광고 매체별 tag 설치 여부 확인
  2. 설치 여부를 tag_valid 에 저장 

- `get_main()`
  1.  

###
### DB
