## Car Scraper
This project is a car scraper designed to search for used Toyota Sequoia 
cars imported from the USA and notify the client about unique listings 
via a Telegram channel. The scraper retrieves car information from the
https://auto.ria.com and https://bidfax.info website and provides updates on price changes and sold 
listings.

### System Requirements
Operating System: Linux
Python 3.10

### Installation
- Clone the repository to your local machine:
```bash
git clone https://github.com/inrock1/scrap-ria.com
```

- Navigate to the project directory:
```bash
cd car-scraper
```

- Install the required Python packages:
```bash
pip install -r requirements.txt
```

Join to telegram chanel: https://t.me/+mpkb-7PZs1UzMzZi


Ask the autor for .env file and put it in project folder.
## Usage
To run the car scraper, execute the following command in the project directory:

```bash
python scraper.py
```
The scraper will start searching for used Toyota Sequoia cars on auto.ria.com with the specified search filters. It will periodically check for new listings, price changes, and sold listings every 10 minutes.

The scraper will send notifications to the configured Telegram channel for unique car listings. Each notification will include a compact and harmonious message containing multiple car photos as an album, along with the following information:

- Car model name  
- Price  
- Photos car in Ukraine
- Link to the car listing on https://auto.ria.com  
- Link to the page with car photos from the US auction
- Photos car in USA  
If a price change or a sold listing is detected for a previously notified car, the scraper will also send a message to the Telegram channel.
