from bs4 import BeautifulSoup as bs
import requests


def send_get_request(url: str, request:requests.session, decode: bool = True):
    response = request.get(url)
    

    if decode:
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
    else:
        soup = bs(response.text, 'html.parser')

    return soup