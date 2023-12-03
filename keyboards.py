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
        # Chanel routs
        [KeyboardButton(text='/add_channel')],
        # [KeyboardButton(text='/remove_channel')],
        # [KeyboardButton(text='/list_subscribers')],
        # # Users
        # [KeyboardButton(text='/ban_subscriber')],
        # [KeyboardButton(text='/unban_subscriber')],
        # # Money
        # [KeyboardButton(text='/check_balance')],
        # [KeyboardButton(text='/withdraw')],
    ],
    resize_keyboard=True,
)

subscriber_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        # Chanel routs
        [KeyboardButton(text='/list_channels')],
        # [KeyboardButton(text='/subscribe')],
        # [KeyboardButton(text='/unsubscribe')],
        #
        # [KeyboardButton(text='/deposit')],
    ],
    resize_keyboard=True,
)

admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/approve_channels')],
    ],
    resize_keyboard=True,
)


def generate_list_of_channels(page: int = 0):

    keyboard_builder = InlineKeyboardBuilder()

    for _ in range(page, page + 5):
        subscribe_button = InlineKeyboardButton(
            text=database.channels[_],
            url='http://aboba.com',
        )

        keyboard_builder.row(subscribe_button)

    next_button = InlineKeyboardButton(
        text='Next page >>>',
        url='http://aboba.com'
    )

    previous_button = InlineKeyboardButton(
        text='Previous page <<<',
        url='http://aboba.com',
    )

    keyboard_builder.row(next_button)
    keyboard_builder.row(previous_button)

    return keyboard_builder.as_markup()

