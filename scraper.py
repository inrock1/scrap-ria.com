import asyncio
import sqlite3
import requests
import cloudscraper
import time
import random

from bs4 import BeautifulSoup
from dataclasses import dataclass

from notification import send_new_car_notification, change_price_notification

filter_url = "https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&categories.main.id=1&brand.id[0]=79&model.id[0]=2104&country.import.usa.not=0&price.currency=1&abroad.not=0&custom.not=1&damage.not=0&page=0&size=100"

conn = sqlite3.connect('car_data.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    autoId INTEGER UNIQUE,
                    brand TEXT,
                    price INTEGER,
                    photo_urls TEXT,
                    car_url TEXT,
                    auction_url TEXT,
                    usa_photo_urls TEXT
                )''')

@dataclass
class Car:
    autoId: int
    brand: str
    prise_USD: int
    photo_urls: list[str]
    car_url: str
    auction_url: str
    usa_photo_urls: list[str]


def get_usa_photo(auction_url: str) -> list[str]:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(auction_url)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")

    photo_elements = soup.select('div.full-screens img')
    usa_photo_urls = ["https://bidfax.info" + photo['src'] for photo in photo_elements]

    return usa_photo_urls


def get_car(car_url: str, auto_id: int) -> Car | None:
    page = requests.get(car_url)
    soup = BeautifulSoup(page.content, "html.parser")
    car = Car(autoId=auto_id, brand="Toyota Sequoia", car_url=car_url, prise_USD=None, photo_urls=[], auction_url=None, usa_photo_urls=[])

    # Extract price
    price_element = soup.find("div", class_="price_value")
    price_text = price_element.strong.text.strip()

    if "$" in price_text:
        price_numeric = ''.join(filter(str.isdigit, price_text))
        car.prise_USD = int(price_numeric)
    else:
        alternative_price_element = soup.find("span", class_="price_value--additional").find("span",
                                                                                             {"data-currency": "USD"})
        if alternative_price_element is not None:
            alternative_price_text = alternative_price_element.text.strip()
            price_numeric = ''.join(filter(str.isdigit, alternative_price_text))
            car.prise_USD = int(price_numeric)
        else:
            car.prise_USD = None

    # Skip car with the same auto_id and prise if exists in the database
    cursor.execute("SELECT * FROM cars WHERE autoId = ?", (auto_id,))
    existing_car = cursor.fetchone()
    if existing_car and existing_car[3] == car.prise_USD:
        return None

    # Extract photo
    photo_elements = soup.find_all("div", class_="photo-620x465")
    for element in photo_elements[:5]:
        img_element = element.find("img")
        photo_url = img_element["src"]

        if "youtube.com" in photo_url:
            continue

        car.photo_urls.append(photo_url)

    # Extract auction_url
    auction_script = soup.select_one("script[data-bidfax-pathname]")
    script_contents = auction_script.attrs
    part_url = script_contents.get("data-bidfax-pathname")[7:]
    if part_url:
        car.auction_url = "https://bidfax.info" + part_url

    # Extract bidfax image URLs
    if car.auction_url:
        car.usa_photo_urls = get_usa_photo(car.auction_url)

    return car


async def process_car(car):
    cursor.execute("SELECT * FROM cars WHERE autoId = ?", (car.autoId,))
    existing_car = cursor.fetchone()

    # Car doesn't exist in DB, make an entry and send notification
    if existing_car is None:
        cursor.execute(
            '''INSERT INTO cars (autoId, brand, price, photo_urls, car_url, auction_url, usa_photo_urls)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (car.autoId, car.brand, car.prise_USD, ','.join(car.photo_urls), car.car_url, car.auction_url,
             ','.join(car.usa_photo_urls))
        )
        conn.commit()

        await send_new_car_notification(car)

    # Price changed, update database and send notification
    elif existing_car[3] != car.prise_USD:
        cursor.execute(
            '''UPDATE cars SET price = ? WHERE autoId = ?''',
            (car.prise_USD, car.autoId)
        )
        conn.commit()

        await change_price_notification(car)


async def scrap_pages():
    page = requests.get(filter_url)
    soup = BeautifulSoup(page.content, "html.parser")

    car_elements = soup.find_all("section", class_="ticket-item")
    for car_element in car_elements:
        auto_id = car_element["data-advertisement-id"]
        car_url = f"https://auto.ria.com/uk/auto_toyota_sequoia_{auto_id}.html"
        print(car_url)

        car = get_car(car_url, auto_id)
        if car is None:
            continue
        print(car)

        await process_car(car)

        sleep_duration = random.uniform(2, 5)
        await time.sleep(sleep_duration)
    conn.close()

async def run_scraper():
    while True:
        print("Running scraper...")
        await scrap_pages()
        print("Scraper finished.")
        await time.sleep(600)


if __name__ == '__main__':
    asyncio.run(run_scraper())



