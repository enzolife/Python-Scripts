import pandas as pd

global country_list
country_list = ['sg', 'my', 'tw', 'id', 'th']

for index, country in enumerate(country_list):
    print(str(index) + ' ' + country)
    country_list = country_list.remove(country)