import asyncio
import os
import re

from config import bot_token, channel_id
from telegram import Bot
from telegram import InputMediaPhoto
from database.engine import get_db
from database.models import Photo as PhotoDB


db = get_db()

bot = Bot(token=bot_token)
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def new_car_create_message(
        title: str,
        link: str,
        car_id: str,
        price: str,
        odometer: str,
        location: str,
        auction_url: str
) -> None:
    photo_path = db.query(PhotoDB).filter_by(car_id=car_id).all()
    photo_paths = [
        os.path.join(parent_folder, photo.path) for photo in photo_path
    ]
    media_group = [
        InputMediaPhoto(open(photo_path, 'rb')) for photo_path in photo_paths
    ]

    if auction_url:
        auction_link = f"<a href='{auction_url}'>clearvin</a>"
    else:
        auction_link = "vin code unavailable"

    message = (
        f"<a href='{link}'>{title}</a>\n"
        f"💵 {price}\n"
        f"⚙️ {odometer} тис. км\n"
        f"📌 {location}\n"
        f"🇺🇸 {auction_link}"
    )
    try:
        await bot.send_media_group(
            chat_id=channel_id,
            media=media_group,
            caption=message,
            parse_mode='HTML'
        )
    except Exception as e:
        retry_pattern = re.compile(r'Retry in (\d+) seconds')
        match = retry_pattern.search(str(e))
        if match:
            retry_seconds = int(match.group(1))
            print(f"Telegram flood control exceeded. Retry in {retry_seconds} seconds.")
            await asyncio.sleep(retry_seconds)
            await bot.send_media_group(
                chat_id=channel_id,
                media=media_group,
                caption=message,
                parse_mode='HTML'
            )


async def car_update_price_message(title: str, link: str, price: str) -> None:
    message = (
        f"<a href='{link}'>{title}</a>\n"
        f"price change: {price}"
        )
    await bot.send_message(chat_id=channel_id, text=message, parse_mode='HTML')


async def car_sold_message(title: str, link: str) -> None:
    message = f"Car <a href='{link}'>{title}</a> was sold"
    await bot.send_message(chat_id=channel_id, text=message, parse_mode="HTML")
