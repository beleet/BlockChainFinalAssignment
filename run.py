# import asyncio
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters.command import Command
#
# import enum
# import messages
# import keyboards
# import config
#
#
# # TODO:
# # запустить базу данных, протестить на нескольких аккаунтах
# # сделать кнопки по-человечески
# # админ: супервизорские роуты, вывести средства, ?назначить другого админа?
# # роуты: сменить язык - если останется время
# # нотифаи: вы забанены, разбанены, срок вашей подписки истекает/истёк
#
#
# bot = Bot(token=config.TOKEN)
# dp = Dispatcher()
#
# LANGUAGE = 'en'
#
#
# class UserRole(enum.Enum):
#     """
#     Enumerator, defines the role of the bots user.
#     Admin:
#         supervisor, have full access to the database, have possibility to ban/unban any user, approve the channel.
#     Author:
#         creator of the channel, who adds his channel, have possibility to ban/unban subscriber, change the price
#         for the subscription, withdraw money for subscription.
#     Subscriber:
#         user, who decided to follow authors private channel, can subscribe/unsubscribe.
#     """
#
#     ADMIN = 0
#     AUTHOR = 1
#     SUBSCRIBER = 2
#
#
# @dp.message(Command('help'))
# async def help(message: types.Message):
#     # TODO: прописать документацию и вывести в отдельный файл
#     await message.answer(
#         '/start - start\n'
#         '/help - help\n'
#         '/change_role - change role\n'
#         'тыры пыры'
#     )
#
#
# @dp.message(Command('start', 'change_role'))
# async def start(message: types.Message):
#     await message.answer(
#         messages.greeting[LANGUAGE],
#         reply_markup=keyboards.select_role_keyboard,
#     )
#
#
# @dp.message(Command('author'))
# async def author_menu(message: types.Message):
#     await message.answer(
#         'This is your author menu',
#         reply_markup=keyboards.author_main_keyboard,
#     )
#
#
# @dp.message(Command('subscriber'))
# async def subscriber_menu(message: types.Message):
#     await message.answer(
#         'This is your subscriber menu',
#         reply_markup=keyboards.subscriber_main_keyboard,
#     )
#
#
# @dp.message(Command('list_channels'))
# async def list_channels(message: types.Message):
#     await message.answer(
#         text='List of available channels',
#         reply_markup=keyboards.generate_list_of_channels(),
#     )
#
#
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == '__main__':
#     asyncio.run(main())


import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config
import asyncio
from aiogram.filters.command import Command
import database


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

items_per_page = 5


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

    await bot.send_message(chat_id, "Список каналов:", reply_markup=keyboard.as_markup())


async def show_channel_info(chat_id, channel_id: int):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text='Subscribe',
        url=f'{config.PAYMENT_SERVER}/channel/{channel_id}'
    ))

    await bot.send_message(
        chat_id,
        text=f'Информация о канале {database.channels[channel_id]["name"]}',
        reply_markup=keyboard.as_markup(),
    )


@dp.message(Command('start'))
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

