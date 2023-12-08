import asyncio
import logging
import sys
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.handlers import CallbackQueryHandler
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
# from aiogram.types.inline_keyboard_button import InlineKeyboardButton
# from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from pydantic import ValidationError, validate_call


form_router = Router()
TOKEN = "6632574068:AAHjKk8v5CYQl_wOAtZVNbHcrfR_uEoFz1g"
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dp.include_router(form_router)
# CHANNEL_USERNAMES = ['@aralashma2030']
# user_subscription_status = {}


class Form(StatesGroup):
    full_name_state = State()
    contact_state = State()
    post_type_state = State()
    content_state = State()
    caption_state = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.full_name_state)
    await message.answer(
        f"Assalomu alekum. Ism va familiyangizni kiriting.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
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
        f"Tel: ",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.contact_state)
async def process_contact(message: Message, state: FSMContext) -> None:
    await state.update_data(contact_state=message.text)
    await state.set_state(Form.post_type_state)
    await message.answer(
        f"Ijodiy ishingizda media file mavjudmi?",
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
        "Juda soz. Ijodiy ishinizni to'liq text ko'rinishida yuboring.",
        reply_markup=ReplyKeyboardRemove(),
    )
    # await show_summary(message=message, positive=False)

    
@form_router.message(Form.content_state)
async def process_dont_like_write_bots2(message: Message, state: FSMContext) -> None:
    await state.update_data(content_state=message.text)
    admin_chat_id = 1157747787

    # Get user data from state
    user_data = await state.get_data()
    full_name = user_data.get("full_name_state", "")
    contact = user_data.get("contact_state", "")
    content = user_data.get("content_state", "")

    message_text = f"Ijodiy ish:\n Kimdan: {full_name}\nBog'lanish: {contact}\n{content}"

    # Create inline keyboard with "Accept" and "Reject" buttons
    try:
        keyboards = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("✅ Qabul qilish", callback_data="accept")], # ;{message.from_user.id};{full_name};{contact};{content}
                [InlineKeyboardButton("❌ Rad etish", callback_data="reject")] #;{message.from_user.id}
            ]
        )
        # Send the message to the admin with the inline keyboard
        await bot.send_message(admin_chat_id, message_text, reply_markup=keyboards)
    except Exception as exc:
        print(exc)

    # Send a confirmation message to the user
    await message.answer(
        "Ijodiy ishingiz adminga yuborildi. Admin maqullasa sizning ijodiy ishingiz @aralashma2030 kanalda elon qilinadi.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.callback_query()
class MyHandler(CallbackQueryHandler):
    async def handle(self) -> Any:
        print(CallbackQueryHandler)
# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('reject;'))
# async def process_reject_callback(callback_query: types.CallbackQuery):
#     user_id = int(callback_query.data.split(';')[1])
#     rejection_message = "Uzr. Sizning ijodiy ishingiz qabul qilinmadi!"
#     await bot.send_message(user_id, rejection_message)

#     await bot.answer_callback_query(callback_query.id, text="Post rejected.")


@form_router.message(Form.post_type_state, F.text.casefold() == "ha")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.update_data(post_type_state='yes')

    await message.reply(
        "Juda soz. Ijodiy ishinizni media ko'rinishida yuboring.",
        reply_markup=ReplyKeyboardRemove(),
    )
# @form_router.message(ContentType=types.ContentType.PHOTO | types.ContentType.VIDEO, state=Form.post_type_state)
# async def process_media_submission(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     file_id = message.photo[-1].file_id if message.photo else message.video.file_id

#     # Update the post type in the state data
#     await state.update_data(post_type_state='media')

#     # Save the media file information to the state data
#     await state.update_data(media_file_id=file_id)

#     await message.answer("Yaxshi, endi media faylingizni yuboring.")
#     await Form.waiting_for_content.set()


@form_router.message(Form.post_type_state)
async def process_unknown_write_bots(message: Message) -> None:
    await message.reply("I don't understand you :(")


# @form_router.message(Form.language)
# async def process_language(message: Message, state: FSMContext) -> None:
#     data = await state.update_data(language=message.text)
#     await state.clear()

#     if message.text.casefold() == "python":
#         await message.reply(
#             "Python, you say? That's the language that makes my circuits light up! 😉"
#         )

#     await show_summary(message=message, data=data)


# async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
#     name = data["name"]
#     language = data.get("language", "<something unexpected>")
#     text = f"I'll keep in mind that, {html.quote(name)}, "
#     text += (
#         f"you like to write bots with {html.quote(language)}."
#         if positive
#         else "you don't like to write bots, so sad..."
#     )
#     await message.answer(text=text, reply_markup=ReplyKeyboardRemove())



async def start():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

asyncio.run(start())
