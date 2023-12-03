from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database


select_role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/author')],
        [KeyboardButton(text='/subscriber')],
    ],
    resize_keyboard=True,
)

author_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/add_channel')],
        # [KeyboardButton(text='/check_balance')],
        # [KeyboardButton(text='/withdraw')],
        [KeyboardButton(text='/change_role')],
    ],
    resize_keyboard=True,
)

subscriber_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        # Chanel routs
        [KeyboardButton(text='/list_channels')],
        # [KeyboardButton(text='/subscribe')],
        # [KeyboardButton(text='/deposit')],
        [KeyboardButton(text='/change_role')],
    ],
    resize_keyboard=True,
)

admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/approve_channels')],
        [KeyboardButton(text='/change_role')],
    ],
    resize_keyboard=True,
)
