import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config
import asyncio
from aiogram.filters.command import Command
import database
import keyboards


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

items_per_page = 5


# -------------------------SERVICE COMMANDS-----------------------------------
@dp.message(Command('help'))
async def help(message: types.Message):
    await message.answer(
        '/start - start\n'
        '/help - help\n'
        '/change_role - change role\n'
        'тыры пыры'
    )


@dp.message(Command('start', 'change_role'))
async def start(message: types.Message):
    await message.answer(
        text='Welcome, please select your role!',
        reply_markup=keyboards.select_role_keyboard,
    )


# -------------------------ADMIN COMMANDS-----------------------------------
@dp.message(Command('admin'))
async def start_command(message: types.Message):
    if message.from_user.id in [1273783566]:
        await message.answer(
            'This is your admin menu',
            reply_markup=keyboards.admin_main_keyboard,
        )


@dp.message(Command('approve_channels'))
async def start_command(message: types.Message):
    await show_channels_to_approve_page(message.chat.id)


async def show_channels_to_approve_page(chat_id, page=0):

    start_index = page * items_per_page
    end_index = start_index + items_per_page
    current_channels = database.channels_to_check[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for channel in current_channels:
        button_text = f"{channel['name']} - {channel['link']}"
        keyboard.row(InlineKeyboardButton(text=button_text, callback_data=f'approve_{channel["id"]}'))

    if page > 0:
        keyboard.row(InlineKeyboardButton(text="<<<", callback_data=f"prevapprove_{page}"))
    if end_index < len(database.channels_to_check):
        keyboard.row(InlineKeyboardButton(text=">>>", callback_data=f"nextapprove_{page}"))

    await bot.send_message(chat_id, "Channels to approve list:", reply_markup=keyboard.as_markup())


async def show_channel_to_approve_info(chat_id, channel_id: int):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Approve', callback_data=f'approve_{channel_id}'))

    await bot.send_message(
        chat_id,
        text=f'{database.channels_to_check[channel_id]}'
    )


@dp.callback_query(lambda c: c.data.startswith('prevapprove'))
async def callback_prev(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await show_channels_to_approve_page(callback_query.message.chat.id, page - 1)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('nextapprove'))
async def callback_next(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await show_channels_to_approve_page(callback_query.message.chat.id, page + 1)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('approve'))
async def callback_subscribe(callback_query: types.CallbackQuery):

    channel_id = int(callback_query.data.split('_')[1])

    channel = database.channels_to_check[channel_id]
    database.channels_to_check.remove(channel)

    channel['id'] = len(database.channels)
    database.channels.append(channel)

    await show_channels_to_approve_page(callback_query.message.chat.id)
    await bot.answer_callback_query(callback_query.id)


# -------------------------AUTHOR COMMANDS-----------------------------------
@dp.message(Command('author'))
async def author_menu(message: types.Message):
    await message.answer(
        'This is your author menu',
        reply_markup=keyboards.author_main_keyboard,
    )


@dp.message(Command('add_channel'))
async def add_channel(message: types.Message):

    args = message.text.split(' ')

    try:
        channel_url = str(args[1])
        channel_description = str(args[2])
        channel_price = int(args[3])
    except (IndexError, ValueError):
        await bot.send_message(
            text='Type /add_channel <url> <description> <subscription cost>',
            chat_id=message.chat.id,
        )
        return

    database.channels_to_check.append(
        {
            'id': len(database.channels_to_check),
            'name': channel_url,
            'description': channel_description,
            'cost': channel_price,
            'link': channel_url,
        }
    )

    await bot.send_message(
        text='Channel successfully added!',
        chat_id=message.chat.id,
    )


# -------------------------SUBSCRIBER COMMANDS-----------------------------------
@dp.message(Command('subscriber'))
async def subscriber_menu(message: types.Message):
    await message.answer(
        'This is your subscriber menu',
        reply_markup=keyboards.subscriber_main_keyboard,
    )


async def show_channels_page(chat_id, page=0):

    start_index = page * items_per_page
    end_index = start_index + items_per_page
    current_channels = database.channels[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for channel in current_channels:
        button_text = f"{channel['name']} - {channel['link']}"
        keyboard.row(InlineKeyboardButton(text=button_text, callback_data=f'subscribe_{channel["id"]}'))

    if page > 0:
        keyboard.row(InlineKeyboardButton(text="<<<", callback_data=f"prev_{page}"))
    if end_index < len(database.channels):
        keyboard.row(InlineKeyboardButton(text=">>>", callback_data=f"next_{page}"))

    await bot.send_message(chat_id, "List of channels:", reply_markup=keyboard.as_markup())


async def show_channel_info(chat_id, channel_id: int):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text='Subscribe',
        url=f'{config.PAYMENT_SERVER}/channel/{channel_id}'
    ))

    await bot.send_message(
        chat_id,
        text=f'Info about channel {database.channels[channel_id]["name"]}',
        reply_markup=keyboard.as_markup(),
    )


@dp.message(Command('list_channels'))
async def start_command(message: types.Message):
    await show_channels_page(message.chat.id)


@dp.callback_query(lambda c: c.data.startswith('prev'))
async def callback_prev(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await show_channels_page(callback_query.message.chat.id, page - 1)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('next'))
async def callback_next(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await show_channels_page(callback_query.message.chat.id, page + 1)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('subscribe'))
async def callback_subscribe(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[1])
    await show_channel_info(callback_query.message.chat.id, channel_id=channel_id)
    await bot.answer_callback_query(callback_query.id)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

