import tenacity
import re
from bs4 import BeautifulSoup
import httpx as httpx
import asyncio
from sqlalchemy.exc import IntegrityError
from database.models import Car as CarDB
from database.models import Photo as PhotoDB
from database.engine import get_db
from format.format_tools import (
    format_price,
    format_location,
    format_url_auction,
    format_car_vin,
)
from telegram_folder.menager import car_update_price_message, car_sold_message

db = get_db()


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_random_exponential(multiplier=1, max=10),
)
async def get_soup_async(url: str, params: dict = None) -> BeautifulSoup:
    async with httpx.AsyncClient() as client:
        if params:
            response = await client.get(url, params=params)
        else:
            response = await client.get(url)
        page = response.content
        return BeautifulSoup(page, "html.parser")


async def get_all_detail_links(base_url: str) -> list:

    params = {
        'indexName': 'auto,order_auto,newauto_search',
        'category_id': 1,
        'marka_id[0]': 79,
        'model_id[0]': 2104,
        'matched_country': 840,
        'abroad': 2,
        'custom': 1,
        'page': 0,
        'countpage': 10
    }
    all_links = []

    while True:
        soup = await get_soup_async(base_url, params=params)
        all_divs_with_links = soup.find_all('div', class_='item ticket-title')
        if not all_divs_with_links:
            return all_links

        all_links += [div.find('a')['href'] for div in all_divs_with_links]

        params['page'] += 1


def process_detail_page(soup: BeautifulSoup, detail_url: str) -> CarDB:

    link = detail_url
    car_id = link.split('_')[-1][:-5]
    title = soup.find('h1', class_='head')['title']
    price = format_price(soup)
    odometer = soup.find(
        'div',
        class_='base-information bold'
    ).text.split(' ')[1]

    location = format_location(soup)
    car_vin = format_car_vin(soup)
    auction_url = format_url_auction(car_vin)

    sold = True if soup.find('div', id='autoDeletedTopBlock') else False

    return CarDB(
        link=link,
        car_id=car_id,
        title=title,
        price=price,
        odometer=odometer,
        location=location,
        car_vin=car_vin,
        auction_url=auction_url,
        sold=sold
    )


def get_all_image_links(soup: BeautifulSoup) -> list:
    div = soup.find('div', class_='preview-gallery mhide')
    webp_sources = div.find_all('source', {'srcset': re.compile(r'.*\.webp')})
    webp_links = [
        source['srcset'].replace("s.webp", "hd.webp")
        for source in webp_sources[:3]
    ]
    return webp_links


async def save_car_to_db(car: CarDB) -> CarDB | None:

    new_car = db.query(CarDB).filter_by(car_id=car.car_id).first()
    if new_car:
        if car.sold and not new_car.sold:
            new_car.sold = True
            await car_sold_message(title=new_car.title, link=new_car.link)

        if getattr(new_car, 'price') != getattr(car, 'price') and not new_car.sold:
            new_car.price = car.price
            db.commit()
            await car_update_price_message(
                title=new_car.title,
                link=new_car.link, price=car.price
            )

        else:
            print(f'Car: {new_car.title} with id: {new_car.car_id} exist!')

    elif not new_car and not car.sold:
        try:
            db.add(car)
            db.commit()
            return db.query(CarDB).filter_by(car_id=car.car_id).first()
        except IntegrityError:
            db.rollback()


def save_photo_path_to_db(images_path: set, car_id: str) -> None:

    for path in images_path:
        photo = PhotoDB(
            path=path,
            car_id=car_id,
        )
        db.add(photo)
        db.commit()


async def process_detail_page_async(
        soup: BeautifulSoup,
        detail_url: str
) -> CarDB:
    return await asyncio.to_thread(process_detail_page, soup, detail_url)


async def get_all_image_links_async(soup: BeautifulSoup):
    return await asyncio.to_thread(get_all_image_links, soup)


async def save_photo_path_to_db_async(images_path: set, car_id: str) -> None:
    await asyncio.to_thread(save_photo_path_to_db, images_path, car_id)
