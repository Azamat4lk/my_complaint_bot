from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

API_TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определяем состояния для FSM
class SendReplyStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message = State()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "✉ Напиши свою жалобу сюда. "
        "Ты можешь отправлять текст, фото, документы и другие файлы — админ всё получит."
    )

@dp.message(Command("reply"))
async def cmd_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    await message.answer("Введите ID пользователя, которому хотите отправить сообщение:")
    await state.set_state(SendReplyStates.waiting_for_user_id)

@dp.message(SendReplyStates.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("ID должен быть числом. Попробуйте ещё раз.")
        return
    user_id = int(message.text)
    await state.update_data(user_id=user_id)
    await message.answer("Отлично! Теперь отправьте сообщение (текст, фото, документ и др.), которое нужно переслать пользователю.")
    await state.set_state(SendReplyStates.waiting_for_message)

@dp.message(SendReplyStates.waiting_for_message, F.content_type.in_(
    [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.AUDIO, ContentType.VOICE,
     ContentType.VIDEO_NOTE, ContentType.STICKER, ContentType.ANIMATION, ContentType.CONTACT, ContentType.LOCATION]))
async def process_message_to_send(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        await message.answer("Произошла ошибка. Попробуйте заново команду /reply")
        await state.clear()
        return

    try:
        # Если текст, отправляем напрямую
        if message.content_type == ContentType.TEXT:
            await bot.send_message(chat_id=user_id, text=message.text)
        else:
            # Для остальных типов пересылаем копированием (сохраняется формат и файлы)
            await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(f"✅ Сообщение отправлено пользователю {user_id}.")
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить сообщение: {e}")

    await state.clear()

@dp.message(SendReplyStates.waiting_for_message)
async def process_unsupported(message: Message):
    await message.answer("⚠ Тип сообщения не поддерживается. Попробуйте отправить текст, фото, документ и др.")

@dp.message()
async def handle_complaint(message: Message):
    user = message.from_user
    user_id_str = str(user.id)
    user_name = f"@{user.username}" if user.username else user.full_name

    header = f"🚨 Жалоба от {user_name}\nID: {user_id_str}\n\n"

    if message.text:
        complaint = header + message.text
        await bot.send_message(ADMIN_ID, complaint)
        await bot.send_message(ADMIN_ID, user_id_str)
        await message.answer("✅ Спасибо! Ваша жалоба отправлена.")
        return

    if message.content_type in (
        ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.AUDIO, ContentType.VOICE,
        ContentType.VIDEO_NOTE, ContentType.STICKER, ContentType.ANIMATION, ContentType.CONTACT, ContentType.LOCATION,
    ):
        await message.forward(ADMIN_ID)
        await bot.send_message(ADMIN_ID, f"🚨 Жалоба от {user_name}\nID: {user_id_str}\n\n*(Это сообщение с вложением от пользователя)*")
        await bot.send_message(ADMIN_ID, user_id_str)
        await message.answer("✅ Ваш файл отправлен администратору.")
        return

    await message.answer(
        "⚠ Тип сообщения не поддерживается. "
        "Пожалуйста, отправьте текст, фото, документ или другой файл."
    )


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())