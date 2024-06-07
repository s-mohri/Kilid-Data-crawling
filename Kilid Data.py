from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import time
import datetime


def setup_database():
    db = sqlite3.connect('housing.db')
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS details (
        ad_id INTEGER PRIMARY KEY,
        published_date TIMESTAMP,
        description TEXT,
        price REAL,
        location TEXT,
        area INTEGER,
        bedrooms INTEGER,
        url TEXT,
        agency TEXT,
        building_age INTEGER,
        building_type TEXT
    )
    ''')
    return db, cursor


def fetch_data(ch):
    url = "https://kilid.com/buy/tehran-satarkhan?listingTypeId=1&location=328363&sort=DATE_DESC&page=0"
    ch.get(url)
    time.sleep(2)
    cards = ch.find_elements(By.XPATH, '//a[contains(@href, "detail")]')

    data = {
        'ad_id': [], 'published_date': [], 'description': [], 'price': [],
        'location': [], 'area': [], 'bedrooms': [], 'url': [], 'agency': [],
        'building_age': [], 'building_type': []
    }

    for card in cards:
        temp = card.text.split('\n')
        if len(temp) >= 8:
            data['ad_id'].append(int(card.get_attribute('href').split('/')[-1]))
            data['published_date'].append(temp[0])
            data['description'].append(temp[1])
            data['price'].append(temp[2].strip('قیمت:').replace(',', ''))
            data['location'].append(temp[3])
            data['building_type'].append(temp[4])
            data['area'].append(temp[5].strip('متر'))
            if 'پارکینگ' in temp[6]:
                data['bedrooms'].append(temp[7].strip('خواب'))
            else:
                data['bedrooms'].append(temp[6].strip('خواب'))
            data['agency'].append(temp[-4])
            data['building_age'].append(None)
            data['url'].append(card.get_attribute('href'))

    return data


def process_dates(dates):
    processed_dates = []
    for date in dates:
        parts = date.split(' ')
        if 'ساعت' in parts:
            delta = datetime.timedelta(hours=int(parts[0]))
        elif 'روز' in parts:
            delta = datetime.timedelta(days=int(parts[0]))
        elif 'ماه' in parts:
            delta = datetime.timedelta(days=30 * int(parts[0]))
        else:
            delta = datetime.timedelta(days=0)
        processed_dates.append((datetime.datetime.utcnow() - delta).strftime('%Y-%m-%d'))
    return processed_dates


def process_prices(prices):
    processed_prices = []
    for price in prices:
        parts = price.split(' ')
        parts = [i for i in parts if i]
        if len(parts) >= 2:
            if parts[1] == 'میلیارد':
                processed_prices.append(float(parts[0]))
            elif parts[1] == 'میلیون':
                processed_prices.append(float(parts[0]))
            else:
                processed_prices.append(0)
        else:
            processed_prices.append(0)
    return processed_prices


def save_to_database(cursor, data):
    for i in range(len(data['ad_id'])):
        cursor.execute('''
        INSERT OR IGNORE INTO details (
            ad_id, published_date, description, price, location,
            area, bedrooms, url, agency, building_age, building_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['ad_id'][i], data['published_date'][i], data['description'][i],
            data['price'][i], data['location'][i], int(data['area'][i]),
            int(data['bedrooms'][i]), data['url'][i], data['agency'][i],
            10, data['building_type'][i]
        ))


def main():
    # Setup WebDriver
    service = Service(ChromeDriverManager().install())
    ch = webdriver.Chrome(service=service)

    try:
        # Setup database
        db, cursor = setup_database()

        # Fetch data
        data = fetch_data(ch)

        # Process data
        data['published_date'] = process_dates(data['published_date'])
        data['price'] = process_prices(data['price'])

        # Save data to database
        save_to_database(cursor, data)

        # Commit and close database
        db.commit()
        cursor.close()
        db.close()
    finally:
        ch.quit()


if __name__ == '__main__':
    main()
