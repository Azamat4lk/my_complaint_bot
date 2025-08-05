from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ContentType
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
    await message.answer("✉ Напиши свою жалобу сюда. Ты можешь отправлять текст, фото, документы и другие файлы — админ всё получит.")

@dp.message()
async def handle_complaint(message: Message):
    user = message.from_user
    # Если это текст — отправляем с подписью
    if message.text:
        complaint = (
            f"🚨 Жалоба от @{user.username or user.first_name} (ID: {user.id}):\n\n{message.text}"
        )
        await bot.send_message(ADMIN_ID, complaint)
        await message.answer("✅ Спасибо! Ваша жалоба отправлена.")
        return
    # Если сообщение содержит медиа или документы — пересылаем админу
    if message.content_type in (
        ContentType.PHOTO,
        ContentType.DOCUMENT,
        ContentType.VIDEO,
        ContentType.AUDIO,
        ContentType.VOICE,
        ContentType.VIDEO_NOTE,
        ContentType.STICKER,
        ContentType.ANIMATION,
        ContentType.CONTACT,
        ContentType.LOCATION,
        # Добавь сюда другие типы, если нужно
    ):
        await message.forward(ADMIN_ID)
        await message.answer("✅ Ваш файл отправлен администратору.")
        return
    # Если что-то не распознано, скажем об этом
    await message.answer("⚠ Тип сообщения не поддерживается. Пожалуйста, отправьте текст, фото, документ или другой файл.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())