from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import requests


def get_product_sales_record(url):
    htmlContent = requests.get(url, verify=False)
    data = htmlContent.text
    jsonD = json.dumps(htmlContent.text)
    jsonL = json.loads(jsonD)


if __name__ == "__main__":
    url = 'https://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?' \
          'callback=jQuery18307810853061944567_1505355496624' \
          '&productId=32326661278' \
          '&type=default&page=1' \
          '&_=1505355583786'
    get_product_sales_record()
