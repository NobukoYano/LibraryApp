import json
import requests

class openBD:
    '''
    openBD API
    '''
    def __init__(self):
        '''
        initialize
        '''
        pass

    def get_json(self, isbn:str) -> dict:
        '''
        extract book info from openBD API
        Parameters
        ----------
        isbn : str
            isbn code without '-'
        Returns
        -------
        json : dic
            books info
            returns None in case of failure
        '''
        # gey json data using web API
        json_api_data = self.__call_web_api(isbn)

        # if it failed
        if json_api_data == None:
            return None
        
        # if it succeed
        if json_api_data[0] == None:
            return None
        # extract summary info.
        json_data = {}
        json_data['isbn'] = json_api_data[0]['summary']['isbn']
        json_data['title'] = json_api_data[0]['summary']['title']
        json_data['publisher'] = json_api_data[0]['summary']['publisher']
        json_data['pubdate'] = json_api_data[0]['summary']['pubdate']
        json_data['cover'] = json_api_data[0]['summary']['cover']
        json_data['author'] = json_api_data[0]['summary']['author']

        # isbnコードが込み入った形で格納されている
        # industryIdentifiers = json_api_data['items'][0]['volumeInfo']['industryIdentifiers']
        # for item in industryIdentifiers:
        #     if item['type'] == 'ISBN_13':
        #         json_data['isbn'] = item['identifier']
        #         break

        return json_data
        
    def __call_web_api(self, isbn:str) -> dict:
        '''
        Calling openBD API, get json data of the book
        Parameters
        ----------
        isbn : str
            isbn code
        Returns
        -------
        json_data : dic
            json data of the book
            returns None in case of failure
        '''
        url = 'https://api.openbd.jp/v1/get?isbn=' + isbn

        # Calling WebAPI 
        response = requests.get(url)

        # Check the status code
        status_code = response.status_code
        if status_code != 200:
            # if failed
            return None

        # if succeed
        json_text = response.text      

        # Exchange into dictionary
        json_data = json.loads(json_text)

        return json_data