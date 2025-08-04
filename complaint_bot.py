from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

API_TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("✉ Напиши свою жалобу сюда. Администратор её получит.")

@dp.message()
async def handle_complaint(message: Message):
    user = message.from_user
    complaint = (
        f"🚨 Жалоба от @{user.username or user.first_name} (ID: {user.id}):\n\n{message.text}"
    )
    await bot.send_message(ADMIN_ID, complaint)
    await message.answer("✅ Спасибо! Ваша жалоба отправлена.")
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())