import re

class Utils:
    
    @staticmethod
    def change_href(main_url:str, row:str):
        ''' 이동 불가능한 url을 outerHTML을 통해 이동 가능한 url로 업데이트
        
        #TODO : 웹 사이트별 다른 HTML코드에서 필요한 url을 추출하는 방법 
        '''
        regex = r'href\s*=\s*[\'"]#\s*[\'"].*?location\.href\s*=\s*[\'"](.*?)[\'"]'
        match = re.search(regex, row['outerHTML'])
        if match and match.group(1) is not None:
            url = main_url + match.group(1) ##TODO : URL이 a.href가 아닌 HTML Code에 있을 경우 HTML Code를 parse하여 url에 붙이기
            # Ex: main_url 'https://www.samsungebiz.com'
        else:
            url = row['href']
        return url
    
    @staticmethod
    def parse_parameter(url:str):
        '''get request log 의 url에 포함된 파라미터를 parse
        return dict (Ex: {name : 'jimmy', age : '26'})
        '''
        param_dict = {}
        while url and '&' in url:
            text, url = url.split('&', maxsplit = 1)
            name, parameter = text.split('=')
            param_dict[name] = parameter
        return param_dict