import asyncio
import telebot
import logging


BOT_TOKEN = "6031099887:AAFZpmF7y1ltGh0b9dFHXUxQfj3cVfFQIYE"
CHANNEL_ID = "-1001904784576"
bot = telebot.TeleBot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

def send_new_car_notification(car):
    media_group = [telebot.types.InputMediaPhoto(media=photo_url) for photo_url in car.photo_urls]

    message = f"👆*Toyota Sequoia*\n" \
              f"💵 {car.prise_USD} $\n" \
              f"🇺🇦 [ria\\.com]({car.car_url})\n" \
              f"🇺🇸 [bidfax]({car.auction_url})"

    bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='MarkdownV2', disable_web_page_preview=True)


def change_price_notification(car):
    media_group = [telebot.types.InputMediaPhoto(media=photo_url) for photo_url in car.photo_urls]

    message = f"👆*Toyota Sequoia*\n" \
              f"💵 new price: {car.prise_USD} $\n" \
              f"🇺🇦 [ria\\.com]({car.car_url})\n" \
              f"🇺🇸 [bidfax]({car.auction_url})"

    bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='MarkdownV2', disable_web_page_preview=True)

