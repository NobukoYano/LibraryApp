import json
import requests
from django.conf import settings



class rakuten:

    def get_json(self, isbn: str) -> dict:
        appid = settings.RAKUTEN_APP_ID

        # API request template
        api = "https://app.rakuten.co.jp/services/api/BooksTotal/"\
              "Search/20170404?format=json&isbnjan={isbnjan}&"\
              "applicationId={appid}"

        # format get api URL
        url = api.format(isbnjan=isbn, appid=appid)

        # execute
        r = requests.get(url)
        # decode to json

        # Check the status code
        status_code = r.status_code
        if status_code != 200:
            # if failed
            return None

        data = json.loads(r.text)

        json_data = {}
        json_data['isbn'] = data['Items'][0]['Item']['isbn']
        json_data['title'] = data['Items'][0]['Item']['title']
        json_data['publisher'] = data['Items'][0]['Item']['publisherName']
        json_data['pubdate'] = data['Items'][0]['Item']['salesDate']
        json_data['cover'] = data['Items'][0]['Item']['largeImageUrl']
        json_data['author'] = data['Items'][0]['Item']['author']

        return json_data
