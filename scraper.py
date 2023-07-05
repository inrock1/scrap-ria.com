import os
import random
import sqlite3
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from scrapingant_client import ScrapingAntClient

from notification import change_price_notification, send_new_car_notification

load_dotenv()
ANT_TOKEN = os.getenv("ANT_TOKEN")

FILTER_URL = "https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&categories.main.id=1&brand.id[0]=79&model.id[0]=2104&country.import.usa.not=0&price.currency=1&abroad.not=0&custom.not=1&damage.not=0&page=0&size=100"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}

conn = sqlite3.connect("car_data.db")
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    autoId INTEGER UNIQUE,
                    brand TEXT,
                    price INTEGER,
                    photo_urls TEXT,
                    car_url TEXT,
                    auction_url TEXT,
                    usa_photo_urls TEXT,
                    main_price TEXT
                )"""
)


@dataclass
class Car:
    autoId: int
    brand: str
    main_price: str
    prise_USD: int
    photo_urls: list[str]
    car_url: str
    auction_url: str
    usa_photo_urls: list[str]


def get_usa_photo(auction_url: str) -> list[str]:
    try:
        client = ScrapingAntClient(token=ANT_TOKEN)
        response = client.general_request(auction_url)
        content = response.content
        soup = BeautifulSoup(content, "html.parser")

        photo_elements3 = soup.select("div.full-screens img")
        usa_photo_urls = ["https://bidfax.info" + photo["src"] for photo in photo_elements3]

        return usa_photo_urls
    except requests.RequestException as e:
        print("Error during request:", e)
    except Exception as e:
        print("An error occurred:", e)
    return []


def get_car(car_url: str, auto_id: int) -> Car | None:
    try:
        page = requests.get(car_url, headers=HEADERS)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        car = Car(
            autoId=auto_id,
            brand="Toyota Sequoia",
            car_url=car_url,
            main_price="",
            prise_USD=None,
            photo_urls=[],
            auction_url=None,
            usa_photo_urls=[],
        )

        # Extract price
        price_element = soup.find("div", class_="price_value")
        price_text = price_element.strong.text.strip()
        car.main_price = price_text

        if "$" in price_text:
            price_numeric = "".join(filter(str.isdigit, price_text))
            car.prise_USD = int(price_numeric)
        else:
            alternative_price_element = soup.find(
                "span", class_="price_value--additional"
            ).find("span", {"data-currency": "USD"})
            if alternative_price_element is not None:
                alternative_price_text = alternative_price_element.text.strip()
                price_numeric = "".join(filter(str.isdigit, alternative_price_text))
                car.prise_USD = int(price_numeric)
            else:
                car.prise_USD = None

        cursor.execute("SELECT * FROM cars WHERE autoId = ?", (auto_id,))
        existing_car = cursor.fetchone()

        # Skip car with the same auto_id and prise if exists in the database
        if existing_car and existing_car[8] == car.main_price:
            return None

        # Extract photo
        image_elements = soup.find_all("div", class_="photo-620x465")
        for element in image_elements[:5]:
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
        if (car.auction_url and existing_car is None) or (
            car.auction_url and existing_car[7] == []
        ):
            car.usa_photo_urls = get_usa_photo(car.auction_url)

        return car
    except requests.RequestException as e:
        print("Error during page request:", e)
    except Exception as e:
        print("An error occurred:", e)
    return None


def process_car(car):
    cursor.execute("SELECT * FROM cars WHERE autoId = ?", (car.autoId,))
    existing_car = cursor.fetchone()

    # Car doesn't exist in DB, make an entry and send notification
    if existing_car is None:
        cursor.execute(
            """INSERT INTO cars (autoId, brand, main_price, price, photo_urls, car_url, auction_url, usa_photo_urls)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                car.autoId,
                car.brand,
                car.main_price,
                car.prise_USD,
                ",".join(car.photo_urls),
                car.car_url,
                car.auction_url,
                ",".join(car.usa_photo_urls),
            ),
        )
        conn.commit()

        send_new_car_notification(car)

    # Price changed, update database and send notification
    elif existing_car[8] != car.main_price:
        cursor.execute(
            """UPDATE cars SET main_price = ?, price = ? WHERE autoId = ?""",
            (car.main_price, car.prise_USD, car.autoId),
        )
        conn.commit()

        change_price_notification(car)


def scrap_pages():
    try:
        page = requests.get(FILTER_URL, headers=HEADERS)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")

        car_elements = soup.find_all("section", class_="ticket-item")
        for car_element in car_elements:
            auto_id = car_element["data-advertisement-id"]
            car_url = f"https://auto.ria.com/uk/auto_toyota_sequoia_{auto_id}.html"
            print("checking: ", car_url)

            car = get_car(car_url, auto_id)
            if car is None:
                continue
            print("detected new car or change prise: ", car)

            process_car(car)

            sleep_duration = random.uniform(2, 5)
            time.sleep(sleep_duration)
    except requests.RequestException as e:
        print("Error during advertisement page request:", e)
    except Exception as e:
        print("An error occurred during page scraping:", e)


def run_scraper():
    try:
        while True:
            print("Running scraper...")
            scrap_pages()
            print("Scraper finished. Waiting 10 minutes...")
            time.sleep(600)
    except KeyboardInterrupt:
        print("Scraper interrupted by user.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_scraper()
