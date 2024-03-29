from aiogram import Dispatcher, Bot

from database import Database
from config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

db = Database('db/db.db')
