from aiogram import Bot, Dispatcher, F, Router, html, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from typing import Any, Dict
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import asyncio
import logging
import sys


form_router = Router()
TOKEN = "6632574068:AAHjKk8v5CYQl_wOAtZVNbHcrfR_uEoFz1g"
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTM proxy='http://proxy.server:3128')
dp = Dispatcher()
dp.include_router(form_router)

class Form(StatesGroup):
    full_name_state = State()
    contact_state = State()
    post_type_state = State()
    content_state = State()
    caption_state = State()
    media_id_state = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.full_name_state)
    await message.answer(
        f"✋ Assalomu alekum. Ism va familiyangizni kiriting.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Bekor qilindi.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.full_name_state)
async def process_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name_state=message.text)
    await state.set_state(Form.contact_state)
    await message.answer(
        f"📞 Tel: ",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.contact_state)
async def process_contact(message: Message, state: FSMContext) -> None:
    await state.update_data(contact_state=message.text)
    await state.set_state(Form.post_type_state)
    await message.answer(
        f"✍ Ijodiy ishingizda media file mavjudmi?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ha"),
                    KeyboardButton(text="Yo'q"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(Form.post_type_state, F.text.casefold() == "yo'q")
async def process_dont_like_write_bots1(message: Message, state: FSMContext) -> None:
    await state.update_data(post_type_state='no')
    await state.set_state(Form.content_state)
    await message.answer(
        "✍ Juda soz. Ijodiy ishinizni to'liq text ko'rinishida yuboring.",
        reply_markup=ReplyKeyboardRemove(),
    )
    
@form_router.message(Form.content_state)
async def process_dont_like_write_bots2(message: Message, state: FSMContext) -> None:
    await state.update_data(content_state=message.text)
    admin_chat_id = 177356633
    user_data = await state.get_data()
    full_name = user_data.get("full_name_state", "")
    contact = user_data.get("contact_state", "")
    content = user_data.get("content_state", "")
    message_text = f"✍ Ijodiy ish:\n🧓 Kimdan: {full_name}\n📞 Bog'lanish: {contact}\n{content}"
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept;{message.from_user.id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject;{message.from_user.id}")]
        ]
    )
    await bot.send_message(admin_chat_id, message_text, reply_markup=keyboards)
    await message.answer(
        "✅ Ijodiy ishingiz adminga yuborildi. 👨‍💻 Admin maqullasa sizning ijodiy ishingiz @aralashma2030 kanalda elon qilinadi.",
        reply_markup=ReplyKeyboardRemove(),
    )

@dp.callback_query(lambda query: query.data.startswith('accept;'))
async def process_accept_callback(query: types.CallbackQuery):
    user_id = int(query.data.split(';')[1])
    message_id = query.message.message_id
    acception_message = "👏 Tabriklaymiz. 🫵 Sizning ijodiy ishingiz qabul qilindi!"
    await bot.forward_message(chat_id='@aralashma2030', from_chat_id=177356633, message_id=int(message_id), )
    await bot.send_message(user_id, acception_message)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.answer_callback_query(query.id, text="✅ Post qabul qilindi.")


@dp.callback_query(lambda query: query.data.startswith('reject;'))
async def process_reject_callback(query: types.CallbackQuery):
    user_id = int(query.data.split(';')[1])
    rejection_message = "😢 Uzr. 🫵 Sizning ijodiy ishingiz qabul qilinmadi!"
    await bot.send_message(user_id, rejection_message)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.answer_callback_query(query.id, text="🪓 Post rad etildi.")


@form_router.message(Form.post_type_state, F.text.casefold() == "ha")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.update_data(post_type_state='yes')
    await state.set_state(Form.media_id_state)
    await message.reply(
        "✍ Juda soz. Ijodiy ishinizni media ko'rinishida yuboring.",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.media_id_state)
async def process_dont_like_write_bots2(message: Message, state: FSMContext) -> None:
    if message.photo: media_id = message.photo[-1].file_id
    elif message.video: media_id = message.video.file_id
    else: media_id = None
    await state.update_data(media_id_state=media_id)
    admin_chat_id = 177356633

    user_data = await state.get_data()
    full_name = user_data.get("full_name_state", "")
    contact = user_data.get("contact_state", "")
    user_id = message.from_user.id
    caption = f"Ijodiy ish:\n🧓 Kimdan: {full_name}\n📞 Bog'lanish: {contact}\n"
    keyboards = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"m_accept;{message.from_user.id};{message.message_id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"m_reject;{message.from_user.id};{message.message_id}")]
        ]
    )
    await bot.send_message(admin_chat_id, text=caption, reply_markup=keyboards)
    await bot.forward_message(chat_id=admin_chat_id, from_chat_id=user_id, message_id=message.message_id)
    await message.answer(
        "✅ Ijodiy ishingiz adminga yuborildi. 👨‍💻 Admin maqullasa sizning ijodiy ishingiz @aralashma2030 kanalda elon qilinadi.",
        reply_markup=ReplyKeyboardRemove(),
    )

@dp.callback_query(lambda query: query.data.startswith('m_accept;'))
async def process_accept_callback(query: types.CallbackQuery):
    user_id = int(query.data.split(';')[1])
    message_id = query.message.message_id
    acception_message = "👏 Tabriklaymiz. 🫵 Sizning ijodiy ishingiz qabul qilindi!"
    await bot.forward_message(chat_id='@aralashma2030', from_chat_id=177356633, message_id=int(message_id))
    await bot.forward_message(chat_id='@aralashma2030', from_chat_id=177356633, message_id=int(message_id)+1)
    await bot.send_message(user_id, acception_message)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=int(message_id)+1)
    await bot.answer_callback_query(query.id, text="✅ Post qabul qilindi.")


@dp.callback_query(lambda query: query.data.startswith('m_reject;'))
async def process_reject_callback(query: types.CallbackQuery):
    message_id = query.message.message_id
    user_id = int(query.data.split(';')[1])
    rejection_message = "😢 Uzr. 🫵 Sizning ijodiy ishingiz qabul qilinmadi!"
    await bot.send_message(user_id, rejection_message)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=int(message_id)+1)
    await bot.answer_callback_query(query.id, text="🪓 Post rad etildi.")


async def start():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

asyncio.run(start())
