from _pdf_utils import image_text_collect
import asyncio
import aiofiles
import platform
import os

dir_path = [os.path.join("junior_archives", "out","5", "imgs"), ]

async def collect():
    for d in dir_path:
        file_list = os.listdir(d)
        for file in file_list:
            print(file)
            text = await image_text_collect(os.path.join(d, file))
            async with aiofiles.open(os.path.join(d, file)+".txt", mode="w+", encoding="utf-8-sig") as f:
                await f.write(text)
                await f.close()

if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(collect())