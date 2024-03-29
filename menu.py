from aiogram import types
from loader import db
import utils

back = types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
back_menu = types.InlineKeyboardMarkup(inline_keyboard=[[back]])

post_back = types.InlineKeyboardButton(text='⬅️ Назад', callback_data='post_back')
post_back_menu = types.InlineKeyboardMarkup(inline_keyboard=[[post_back]])

def get_main_menu():
    chanel_data = db.get_data(table='channels')
    if chanel_data:
        chanel_name = chanel_data[0]['name']
    else:
        chanel_name = ('❌ Не подключен \n\n'
                       'Для подключения добавьте бота в канал как администратора и введите команду /connect')

    text = (f'Главное меню \n\n'
            f'📜 Канал для публикаций постов: *{chanel_name}*')

    btn_1 = types.InlineKeyboardButton(text='💬 Мои посты', callback_data='my_posts')
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[btn_1]])

    return text, kb


def get_posts_menu():
    posts = db.get_data(table='posts')

    text_caption = ('Ваши посты \n\n'
            '🟢 - Пост уже опубликован \n'
            '🟡 - Пост еще не опубликован')

    btns = []

    for post in posts:
        status = '🟢' if utils.is_past_moscow_time(post['time']) else '🟡'
        text = f'{post["time"]} {status} {post["text"][:18]}...'
        btns.append([types.InlineKeyboardButton(text=text, callback_data=f'view:{post["id"]}')])

    add = types.InlineKeyboardButton(text='➕', callback_data='add')
    btns.append([add, back])

    kb = types.InlineKeyboardMarkup(inline_keyboard=btns)

    return text_caption, kb


def get_post_view_menu(post_id):
    btn = types.InlineKeyboardButton(text='👌 Изменить время публикации', callback_data=f'edit:{post_id}')
    btn_2 = types.InlineKeyboardButton(text='❌ Удалить', callback_data=f'delete:{post_id}')

    kb = types.InlineKeyboardMarkup(inline_keyboard=[[btn], [btn_2], [post_back]])

    return kb