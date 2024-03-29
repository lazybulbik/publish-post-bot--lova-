import asyncio
import time
from threading import Thread
from datetime import datetime

from aiogram.types import MessageEntity
from aiogram import types

import utils
from loader import *


async def loop():
    print('loop work')
    while True:
        if db.get_data(table='channels'):
            chanel_id = db.get_data(table='channels')[0]['id']
            posts = db.get_data(table='posts')

            for post in posts:
                publish_time = post['time']
                curent_time = utils.get_moscow_time()

                if publish_time == curent_time:
                    type = post['type']

                    if type == 'text':
                        await bot.send_message(chanel_id, post['text'], entities=eval(post['ent']))

                    elif type == 'photo':
                        if len(post['media'].split()) > 1:
                            md = []
                            count = 1
                            for i in post['media'].split():
                                if count == 1:
                                    md.append(types.InputMediaPhoto(media=i, caption=post['text'], caption_entities=eval(post['ent'])))
                                else:
                                    md.append(types.InputMediaPhoto(media=i))
                                count += 1

                            await bot.send_media_group(chanel_id, md)
                        else:
                            await bot.send_photo(chanel_id, post['media'], caption=post['text'], caption_entities=eval(post['ent']))

                    elif type == 'video':
                        await bot.send_video(chanel_id, post['media'], caption=post['text'], caption_entities=eval(post['ent']))
                        print('post_video')

        await asyncio.sleep(60)
