import os
import time

import telebot
from telebot import apihelper
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1001904784576"
bot = telebot.TeleBot(token=BOT_TOKEN)


def send_new_car_notification(car):
    media_group = [
        telebot.types.InputMediaPhoto(media=photo_url) for photo_url in car.photo_urls
    ]
    message = (
        f"👇*Toyota Sequoia*\n"
        f"💵 {car.prise_USD} $\n"
        f"🇺🇦 [ria\\.com]({car.car_url})\n"
        f"🇺🇸 [bidfax]({car.auction_url})"
    )
    try:
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
        bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
    except apihelper.ApiTelegramException as e:
        if e.result.status_code == 429:  # Too Many Requests error
            retry_after = int(e.result.headers.get("retry-after", 5))
            print(f"Too Many Requests: Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            send_new_car_notification(car)  # Retry the notification
        else:
            raise e

    if car.usa_photo_urls:
        media_group_usa = [
            telebot.types.InputMediaPhoto(media=photo_url)
            for photo_url in car.usa_photo_urls[:4]
        ]
        message2 = f"Previous photos from auction in USA👇"
        try:
            bot.send_message(chat_id=CHANNEL_ID, text=message2, parse_mode="MarkdownV2")
            bot.send_media_group(chat_id=CHANNEL_ID, media=media_group_usa)
        except apihelper.ApiTelegramException as e:
            if e.result.status_code == 429:  # Too Many Requests error
                retry_after = int(e.result.headers.get("retry-after", 5))
                print(f"Too Many Requests: Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                send_new_car_notification(car)  # Retry the notification
            else:
                raise e

def change_price_notification(car):
    media_group = [
        telebot.types.InputMediaPhoto(media=photo_url) for photo_url in car.photo_urls
    ]

    message = (
        f"👆*Toyota Sequoia*\n"
        f"💵 new price: {car.prise_USD} $\n"
        f"🇺🇦 [ria\\.com]({car.car_url})\n"
        f"🇺🇸 [bidfax]({car.auction_url})"
    )

    try:
        bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    except apihelper.ApiTelegramException as e:
        if e.result.status_code == 429:  # Too Many Requests error
            retry_after = int(e.result.headers.get("retry-after", 5))
            print(f"Too Many Requests: Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            change_price_notification(car)  # Retry the notification
        else:
            raise e