from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import json


def urlopen_request(request, timeout=10):
    try:
        with urlopen(request) as response:
            body = response.read()
            print(response.status, body)
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print('Request timed out')
    else:
        response_json = body.decode('utf-8')
        response_dic = json.loads(response_json)
        return response_dic
