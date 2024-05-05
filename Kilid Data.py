from selenium import webdriver
import sqlite3
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
service = Service(ChromeDriverManager().install())

ch = webdriver.Chrome(service=service)

db = sqlite3.connect('')
cursor = db.cursor()
url: str = "https://kilid.com/buy-apartment/tehran-shahrak_qarb"
ch.maximize_window()
ch.get(url)
time.sleep(2)
info = ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')

for elem in info:
    print(elem.text)
    print('-' * 40)
urls = [elem.get_attribute('href') for elem in ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')]
for u in urls:
    print(u)
