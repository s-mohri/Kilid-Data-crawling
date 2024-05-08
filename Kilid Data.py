from selenium import webdriver
import sqlite3
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
service = Service(ChromeDriverManager().install())

ch = webdriver.Chrome(service=service)

db = sqlite3.connect('housing')
cursor = db.cursor()
query = 'CREATE TABLE IF NOT EXISTS details '\
    '(ad_id INTEGER, '\
    'published_date TIMESTAMP, '\
    'description TEXT, '\
    'price TEXT'\
    'location TEXT, '\
    'area TEXT, '\
    'bedrooms TEXT, ' \
    'url TEXT, ' \
    'agency TEXT, ' \
    'Building_age INTEGER, ' \
    'PRIMARY KEY (ad_id))'

cursor.execute(query)
url: str = "https://kilid.com/buy-apartment/tehran-shahrak_qarb"
ch.maximize_window()
ch.get(url)
time.sleep(2)
published_time = list()
description = list()
price = list()
location = list()
building_type = list()
area = list()
bedrooms = list()
urls = list()
ad_id = list()
agency = list()
building_age = list()

info = ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')

for elem in info:
   temp = elem.text.split('\n')
   agency.append(temp[-1])
   # published_time.append(temp[1])
   description.append(temp[2])
   price.append(temp[3].strip('قیمت:'))
   location.append(temp[4])
   building_type.append(temp[5])
   area.append(temp[6].strip('متر'))
   bedrooms.append(temp[7].strip('خواب'))

urls = [elem.get_attribute('href') for elem in ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')]
ad_id = [int(elem.get_attribute('href').split('/')[-1]) for elem in
         ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')]
db.commit()
cursor.close()
db.close()
