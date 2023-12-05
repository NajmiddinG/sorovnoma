import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, Contact, InputFile
from aiogram.utils.markdown import hbold
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.contrib.middlewares import UserIdMiddleware
import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Your token
TOKEN = '6632574068:AAHjKk8v5CYQl_wOAtZVNbHcrfR_uEoFz1g'

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(LoggingMiddleware())
# dp.middleware.setup(UserIdMiddleware())

CHANNEL_USERNAMES = ['@aralashma2030']
user_subscription_status = {}

# SQLite Database initialization
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    user_id INTEGER,
    contact_number TEXT,
    post_type TEXT,
    post_content TEXT,
    caption TEXT
)
''')
conn.commit()


class Form(StatesGroup):
    waiting_for_contact = State()
    waiting_for_post_type = State()
    waiting_for_content = State()
    waiting_for_caption = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if not await is_user_subscribed_to_all_channels(user_id):
        # User is not subscribed to all channels, send a message with channel buttons
        await send_channel_subscription_message(message.chat.id)
        return

    await message.answer(f"Salom, {hbold(message.from_user.full_name)}!\n"
                         "Ijodiy ishingizni yuboring(text, rasm) ...")
    await Form.waiting_for_contact.set()


async def is_user_subscribed_to_all_channels(user_id: int) -> bool:
    for channel_username in CHANNEL_USERNAMES:
        if not await is_user_subscribed(user_id, channel_username):
            return False
    return True


async def is_user_subscribed(user_id: int, channel_username: str) -> bool:
    chat_member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
    return chat_member.status in ['member', 'administrator']


async def send_channel_subscription_message(chat_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for channel_username in CHANNEL_USERNAMES:
        button_text = f"Check {channel_username}"
        callback_data = f"check_subscription:{channel_username}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))

    await bot.send_message(chat_id, "You need to subscribe to all required channels to use this bot.", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: 'check_subscription' in callback_query.data)
async def process_check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    channel_username = callback_query.data.split(":")[1]

    # Check if the user is subscribed to the selected channel
    if await is_user_subscribed(user_id, channel_username):
        await bot.answer_callback_query(callback_query.id, text=f"You are subscribed to {channel_username}! 🎉", show_alert=True)
    else:
        await bot.answer_callback_query(callback_query.id, text=f"You are not subscribed to {channel_username}. Please subscribe and try again.", show_alert=True)


@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=Form.waiting_for_contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact
    user_id = message.from_user.id
    cursor.execute('INSERT INTO posts (user_id, contact_number) VALUES (?, ?)', (user_id, contact.phone_number))
    conn.commit()

    await message.answer("Yaxshi, endi post turini tanlang: text yoki media")
    await Form.waiting_for_post_type.set()


@dp.message_handler(lambda message: message.text.lower() == 'text', state=Form.waiting_for_post_type)
async def process_text_post(message: Message):
    await message.answer("Iltimos, matningizni kiriting:")
    await Form.waiting_for_content.set()


@dp.message_handler(lambda message: message.text.lower() == 'media', state=Form.waiting_for_post_type)
async def process_media_post(message: Message):
    await message.answer("Iltimos, media faylingizni yuboring:")
    await Form.waiting_for_content.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.waiting_for_content)
async def process_text_content(message: Message, state: FSMContext):
    post_content = message.text
    user_id = message.from_user.id
    cursor.execute('UPDATE posts SET post_type = "text", post_content = ? WHERE user_id = ?', (post_content, user_id))
    conn.commit()

    await message.answer("Yaxshi, endi postga izoh qoldiring:")
    await Form.waiting_for_caption.set()


@dp.message_handler(content_types=types.ContentTypes.PHOTO | types.ContentTypes.VIDEO,
                    state=Form.waiting_for_content)
async def process_media_content(message: Message, state: FSMContext):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id

    cursor.execute('UPDATE posts SET post_type = "media", file_id = ? WHERE user_id = ?', (file_id, user_id))
    conn.commit()

    await message.answer("Yaxshi, endi postga izoh qoldiring:")
    await Form.waiting_for_caption.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.waiting_for_caption)
async def process_caption(message: Message, state: FSMContext):
    caption = message.text
    user_id = message.from_user.id
    cursor.execute('UPDATE posts SET caption = ? WHERE user_id = ?', (caption, user_id))
    conn.commit()

    await message.answer("Post muvaffaqiyatli qabul qilindi. "
                         "Agar postni tasdiqlaysiz, uni kanalga yuboraman.")
    await state.finish()

    # Send the post to your user for approval
    await bot.send_message(1157747787, f"User {user_id} has submitted a new post. "
                                      f"Please review and approve if necessary.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    finally:
        cursor.close()
        conn.close()
