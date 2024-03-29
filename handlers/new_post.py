import asyncio

from aiogram import types, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

import menu
import utils
from loader import bot, dp, db
from config import ADMIN_ID


@dp.message(StateFilter('add'), F.text)
async def new_post(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    await user_data['ask_msg'].delete()

    ent = 'None' if not msg.entities else str(msg.entities)

    await state.update_data(text=msg.text, ent=ent, type='text', media='')

    user_data = await state.get_data()
    print(user_data)

    text = (f'Введите время для публикации поста \n\n'
            f'*Учтите, бот живет по московскому времени* \n'
            f'⌚ Время в москве: {utils.get_moscow_time()}')
    ask_msg = await msg.answer(text, reply_markup=menu.back_menu, parse_mode='MARKDOWN')
    await state.update_data(ask_msg=ask_msg)
    await state.set_state('time')


@dp.message(StateFilter('add'), F.photo)
async def new_post(msg: Message, state: FSMContext):
    state_data = await state.get_data()

    if not msg.caption:
        caption = 'Без описания'
    else:
        caption = msg.caption

    if msg.media_group_id:
        if 'temp' not in state_data:
            await state.update_data(temp=[], type='photo')

        state_data = await state.get_data()
        state_data['temp'].append(msg.photo[-1].file_id)

        if len(state_data['temp']) > 1:
            return

        await asyncio.sleep(1.5)

        await state.update_data(media=' '.join(state_data['temp']), text=caption, ent=msg.caption_entities, temp=[])

    else:
        await state.update_data(text=msg.caption, ent=msg.caption_entities, type='photo', media=msg.photo[-1].file_id,
                                temp=[])

    user_data = await state.get_data()
    await user_data['ask_msg'].delete()

    print(user_data)

    text = (f'Введите время для публикации поста \n\n'
            f'*Учтите, бот живет по московскому времени* \n'
            f'⌚ Время в москве: {utils.get_moscow_time()}')
    ask_msg = await msg.answer(text, reply_markup=menu.back_menu, parse_mode='MARKDOWN')
    await state.update_data(ask_msg=ask_msg)
    await state.set_state('time')


@dp.message(StateFilter('add'), F.video)
async def new_post(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    await user_data['ask_msg'].delete()

    if not msg.caption:
        caption = 'Без описания'
    else:
        caption = msg.caption

    await state.update_data(text=caption, ent=msg.caption_entities, type='video', media=msg.video.file_id)

    user_data = await state.get_data()
    print(user_data)

    text = (f'Введите время для публикации поста \n\n'
            f'*Учтите, бот живет по московскому времени* \n'
            f'⌚ Время в москве: {utils.get_moscow_time()}')
    ask_msg = await msg.answer(text, reply_markup=menu.back_menu, parse_mode='MARKDOWN')
    await state.update_data(ask_msg=ask_msg)
    await state.set_state('time')


@dp.message(StateFilter('time'))
async def time(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    await user_data['ask_msg'].delete()

    if utils.validate_time(msg.text):
        new_write = {
            'text': user_data['text'],
            'media': user_data['media'],
            'type': user_data['type'],
            'time': msg.text,
            'ent': str(user_data['ent'])
        }
        db.new_write(new_write, 'posts')

        ok_msg = await msg.answer('✅ Пост успешно добавлен')
        await asyncio.sleep(1.5)
        await ok_msg.delete()
        text, kb = menu.get_posts_menu()
        await msg.answer(text, reply_markup=kb, parse_mode='MARKDOWN')

        await state.clear()
    else:
        ask_msg = await msg.answer('❌ Введено некорректное время. Попробуйте еще раз', reply_markup=menu.back_menu)
        await state.update_data(ask_msg=ask_msg)
        return