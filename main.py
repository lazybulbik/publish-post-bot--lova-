import asyncio

from aiogram import types, F
from aiogram.types import Message, CallbackQuery, MessageEntity
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

import menu
from loader import bot, dp, db
from config import ADMIN_ID

from handlers import new_post
from publisher import loop
import utils


@dp.message(Command('start'))
async def start(msg: Message, state: FSMContext):
    if msg.from_user.id in ADMIN_ID:
        text, kb = menu.get_main_menu()

        await msg.answer(text, reply_markup=kb, parse_mode='MARKDOWN')

        user_data = await state.get_state()
        print(user_data)


@dp.channel_post(Command('connect'))
async def connect(msg: types.Message):
    for chanel_id in db.get_data(table='channels'):
        db.delete(filters={'id': chanel_id}, table='channels')

    # await msg.delete()

    db.new_write({'id': msg.chat.id, 'name': msg.chat.full_name}, 'channels')

    await bot.send_message(ADMIN_ID[1], f'✅ Канал *{msg.chat.full_name}* успешно подключен', parse_mode='MARKDOWN')

@dp.message(Command('connect'))
async def connect(msg: types.Message):
    for chanel_id in db.get_data(table='channels'):
        db.delete(filters={'id': chanel_id}, table='channels')

    # await msg.delete()

    db.new_write({'id': msg.chat.id, 'name': msg.chat.full_name}, 'channels')

    await bot.send_message(ADMIN_ID[1], f'✅ Чат *{msg.chat.full_name}* успешно подключен', parse_mode='MARKDOWN')

@dp.message(StateFilter('edit'))
async def edit(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    post_id = user_data['post_id']

    await user_data['ask_msg'].delete()
    await msg.delete()

    if utils.validate_time(msg.text):
        if msg.text.split(':')[0] == '0':
            time_value = f'00:{msg.text.split(":")[1]}'
        else:
            time_value = msg.text
        db.update_data({'time': time_value}, filters={'id': post_id}, table='posts')

        use_msg = await msg.answer(f'Меню взаимодействвия с постом \n\n*Время публикации: {time_value}*', reply_markup=menu.get_post_view_menu(post_id), parse_mode='MARKDOWN')
        await state.update_data(use_msg=use_msg)

        await state.set_state(None)

    else:
        ask_msg = await msg.answer('❌ Введено некорректное время. Попробуйте еще раз', reply_markup=menu.post_back_menu)
        await state.update_data(ask_msg=ask_msg, use_msg=ask_msg)
        return



@dp.callback_query()
async def callbacks(call: CallbackQuery, state: FSMContext):
    print(call.data)

    if call.data == 'my_posts':
        text, kb = menu.get_posts_menu()
        await call.message.edit_text(text, reply_markup=kb, parse_mode='MARKDOWN')

    elif call.data.startswith('back'):
        text, kb = menu.get_main_menu()

        if 'delete' in call.data:
            await call.message.delete()
            await call.message.answer(text, reply_markup=kb, parse_mode='MARKDOWN')
        else:
            await call.message.edit_text(text, reply_markup=kb, parse_mode='MARKDOWN')

        await state.clear()

    elif call.data.startswith('delete:'):
        user_data = await state.get_data()

        db.delete(filters={'id': call.data.split(':')[1]}, table='posts')

        if type(user_data.get('post_msg')) is list:
            for msg in user_data.get('post_msg'):
                await msg.delete()
        else:
            await user_data.get('post_msg').delete()

        await user_data.get('use_msg').delete()

        await call.answer('✅ Пост успешно удален', show_alert=True)

        text, kb = menu.get_posts_menu()
        await call.message.answer(text, reply_markup=kb, parse_mode='MARKDOWN')

        await state.clear()


    elif call.data == 'add':
        await call.message.edit_text('Отправьте сообщение, которое необходимо публиковать', reply_markup=menu.back_menu)

        await state.update_data(ask_msg=call.message)
        await state.set_state('add')

    elif call.data == 'post_back':
        user_data = await state.get_data()

        if type(user_data.get('post_msg')) is list:
            for msg in user_data.get('post_msg'):
                await msg.delete()
        else:
            await user_data.get('post_msg').delete()

        await user_data.get('use_msg').delete()

        text, kb = menu.get_posts_menu()
        await call.message.answer(text, reply_markup=kb, parse_mode='MARKDOWN')


    elif call.data.startswith('edit:'):
        post_id = call.data.split(':')[1]

        text = (f'Введите время для публикации поста \n\n'
                f'*Учтите, бот живет по московскому времени* \n'
                f'⌚ Время в москве: {utils.get_moscow_time()}')

        await call.message.edit_text(text, reply_markup=menu.post_back_menu, parse_mode='MARKDOWN')
        await state.update_data(ask_msg=call.message, post_id=post_id)
        await state.set_state('edit')


    elif call.data.startswith('view:'):
        await call.message.delete()

        post_id = call.data.split(':')[1]
        post = db.get_data(table='posts', filters={'id': post_id})[0]

        if post['type'] == 'photo':
            if len(post['media'].split()) > 1:
                md = []
                count = 1
                for i in post['media'].split():
                    if count == 1:
                        md.append(types.InputMediaPhoto(media=i, caption=post['text'], caption_entities=eval(post['ent'])))
                    else:
                        md.append(types.InputMediaPhoto(media=i))
                    count += 1

                post_msg = await call.message.answer_media_group(md)
            else:
                post_msg = await call.message.answer_photo(post['media'], caption=post['text'], caption_entities=eval(post['ent']))

        elif post['type'] == 'video':
            post_msg = await call.message.answer_video(post['media'], caption=post['text'], caption_entities=eval(post['ent']))

        elif post['type'] == 'text':
            post_msg = await call.message.answer(post['text'], parse_mode='MARKDOWN', disable_web_page_preview=True, entities=eval(post['ent']))


        use_msg = await call.message.answer(f'Меню взаимодействвия с постом \n\n*Время публикации: {post["time"]}*', reply_markup=menu.get_post_view_menu(post_id), parse_mode='MARKDOWN')

        await state.update_data(post_msg=post_msg, use_msg=use_msg)


async def main():
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(loop())

    print('bot start')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
