import asyncio
import telebot
import logging


from main import Car


car = Car(
    autoId=33579103,
    brand="Toyota Sequoia",
    car_url="https://auto.ria.com/uk/auto_toyota_sequoia_33579103.html",
    prise_USD=42900,
    photo_urls=["https://cdn2.riastatic.com/photosnew/auto/photo/toyota_sequoia__473259017f.jpg","https://cdn0.riastatic.com/photosnew/auto/photo/toyota_sequoia__473259010s.jpg","https://cdn2.riastatic.com/photosnew/auto/photo/toyota_sequoia__473259007s.jpg","https://cdn1.riastatic.com/photosnew/auto/photo/toyota_sequoia__473259011s.jpg","https://cdn4.riastatic.com/photosnew/auto/photo/toyota_sequoia__473259009s.jpg"],
    auction_url="https://bidfax.info/toyota/sequoia/7903082-toyota-sequoia-sr5-2019-white-57l-8-vin-5tdzy5g13ks073195.html",
    usa_photo_urls=["https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img1.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img2.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img3.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img4.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img5.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img6.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img7.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img8.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img9.jpg","https://bidfax.info/uploads/posts/2021-02/13/toyota-sequoia-sr-2019-5tdzy5g13ks073195-img10.jpg"]
)

BOT_TOKEN = "6031099887:AAFZpmF7y1ltGh0b9dFHXUxQfj3cVfFQIYE"
CHANNEL_ID = "-1001904784576"
bot = telebot.TeleBot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

async def send_new_car_notification(car):
    media_group = [telebot.types.InputMediaPhoto(media=photo_url) for photo_url in car.photo_urls]

    message = f"👆*Toyota Sequoia*\n" \
              f"💵 {car.prise_USD} $\n" \
              f"🇺🇦 [ria\\.com]({car.car_url})\n" \
              f"🇺🇸 [bidfax]({car.auction_url})"

    bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='MarkdownV2', disable_web_page_preview=True)

async def main():
    await send_new_car_notification(car)

if __name__ == '__main__':
    asyncio.run(main())

