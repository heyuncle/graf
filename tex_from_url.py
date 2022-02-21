import requests
import json

from private_info import *

def tex_from_url(url):
    api_request=requests.post("https://api.mathpix.com/v3/text",data=json.dumps({'src':url}),headers={"app_id":APP_ID,"app_key": APP_KEY,"Content-type": "application/json"})
    return json.loads(api_request.text)["text"]