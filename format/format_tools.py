import httpx as httpx
import os

import tenacity as tenacity
from PIL import Image
from io import BytesIO


def format_price(soup) -> str:
    price = soup.find('div', class_='price_value')
    price_element = price.find('strong', class_='')
    return price_element.text.strip()


def format_location(soup) -> str | None:
    try:
        location = soup.find('section', id='userInfoBlock')
        location = location.find(
            'ul', class_='checked-list unstyle mb-15'
        ).find(
            'li', class_='item'
        ).find(
            'div', class_='item_inner'
        ).text
        return location
    except AttributeError:
        return None


def format_url_auction(vin_code: str) -> str | None:
    url = f"https://www.clearvin.com/ua/payment/prepare/{vin_code}/"
    if vin_code and 'x' not in vin_code:
        return url
    return None


def format_car_vin(soup):
    number = soup.find('span', class_='label-vin')
    if number:
        return number.text


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_random_exponential(multiplier=1, max=10),
)
async def save_images_to_media(webp_links: list, car_id: str) -> set:
    if not os.path.exists(f'media/{car_id}/'):
        os.makedirs(f'media/{car_id}/')

    file_paths = set()
    async with httpx.AsyncClient() as client:
        for idx, link in enumerate(webp_links):
            filename = f"photo_{car_id}_{idx}.jpeg"
            filepath = os.path.join(f'media/{car_id}', filename)

            try:
                response = await client.get(link)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img.thumbnail((img.size[0] // 2, img.size[1] // 2))
                    img.convert("RGB").save(filepath, "JPEG")
                    file_paths.add(filepath)
                else:
                    print(
                        f"Failed to download photo from {link}: Status Code {response.status_code}"
                    )
            except Exception as e:
                print(f"Failed to convert WebP to JPEG for {link}: {e}")

    return file_paths
