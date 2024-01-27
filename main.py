import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from format.format_tools import save_images_to_media
from parser import (
    get_all_detail_links,
    get_soup_async,
    save_car_to_db,
    process_detail_page_async,
    get_all_image_links_async,
    save_photo_path_to_db_async
)
from telegram_folder.menager import new_car_create_message

base_url = "https://auto.ria.com/uk/search/"


async def main() -> None:
    detail_links = await get_all_detail_links(base_url)

    for detail_link in detail_links:
        soup = await get_soup_async(detail_link)
        car_obj = await process_detail_page_async(
            soup=soup,
            detail_url=detail_link
        )
        car_obj = await save_car_to_db(car_obj)

        if car_obj:
            webp_links = await get_all_image_links_async(soup=soup)
            images_path = await save_images_to_media(
                webp_links=webp_links,
                car_id=car_obj.car_id
            )

            if images_path:
                await save_photo_path_to_db_async(
                    images_path=images_path,
                    car_id=car_obj.car_id
                )

                await new_car_create_message(
                    title=car_obj.title,
                    link=car_obj.link,
                    car_id=car_obj.car_id,
                    price=car_obj.price,
                    odometer=car_obj.odometer,
                    location=car_obj.location,
                    auction_url=car_obj.auction_url
                )


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, "interval", seconds=600)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
