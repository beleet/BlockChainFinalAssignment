import enum
import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command

import config
import keyboards

from database import Base, engine, session
from models import User, Subscription, Channel

from smart_contracts.MasterContract.base import MasterContract
from smart_contracts.InstanceContract.base import InstanceContract


Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

master_contract_mumbai = MasterContract(
    provider_url=config.PROVIDER_MUMBAI_URL,
    contract_address=config.MASTER_CONTRACT_MUMBAI_ADDRESS,
)

master_contract_sepolia = MasterContract(
    provider_url=config.PROVIDER_SEPOLIA_URL,
    contract_address=config.MASTER_CONTRACT_SEPOLIA_ADDRESS,
)


class Network(enum.Enum):
    MUMBAI = 1
    SEPOLIA = 2


current_network = Network.MUMBAI

print(current_network)


# -------------------------SERVICE COMMANDS-----------------------------------
@dp.message(Command('help'))
async def help_message(message: types.Message):
    await message.answer(
        '/start - start\n'
        '/help - help\n'
        '/change_role - change role\n'
        '\n'
        'Registration:\n'
        '/set_address <business_address>\n'
    )


@dp.message(Command('start', 'change_role'))
async def start(message: types.Message):

    current_user_telegram_id = message.chat.id

    if not session.query(User).filter_by(telegram_id=current_user_telegram_id).first():
        new_user = User(telegram_id=current_user_telegram_id)
        session.add(new_user)
        session.commit()

    await message.answer(
        text='Welcome, please select your role!',
        reply_markup=keyboards.select_role_keyboard,
    )


@dp.message(Command('change_network'))
async def change_network(message: types.Message):

    global current_network

    if current_network == Network.MUMBAI:
        current_network = Network.SEPOLIA
    else:
        current_network = Network.MUMBAI

    await message.answer(text=f'Network changed to {"MUMBAI" if current_network == Network.MUMBAI else "SEPOLIA"}')



@dp.message(Command('set_address'))
async def set_address(message: types.Message):

    current_user_telegram_id = message.chat.id

    try:
        address = str(message.text.split(' ')[1])
    except (IndexError, ValueError):
        await bot.send_message(
            text='Type /set_address <address>',
            chat_id=message.chat.id,
        )
        return

    if current_network == Network.MUMBAI:

        session.query(User).filter_by(telegram_id=current_user_telegram_id).update({
            "business_address_mumbai": address,
        })

        session.commit()

    else:

        session.query(User).filter_by(telegram_id=current_user_telegram_id).update({
            "business_address_sepolia": address,
        })

        session.commit()

    await message.answer(text='Addresses is successfully set, please register an instance contract!')
    await register(message)


async def register(message: types.Message):

    current_user_telegram_id = message.chat.id
    current_user = session.query(User).filter_by(telegram_id=current_user_telegram_id).first()

    if current_network == Network.MUMBAI:
        address = current_user.business_address_mumbai
    else:
        address = current_user.business_address_sepolia

    register_keyboard = InlineKeyboardBuilder()

    register_keyboard.row(InlineKeyboardButton(
        text='Register',
        url=f'{config.PAYMENT_SERVER}/register/{address}',
    ))

    register_keyboard.row(InlineKeyboardButton(
        text='Check registration',
        callback_data=f'checkregister_{current_user_telegram_id}'
    ))

    await message.answer(
        text='1. Follow link\n'
             '2. Wait for Metamask approval\n'
             '3. Check your registration',
        reply_markup=register_keyboard.as_markup(),
    )


@dp.callback_query(lambda c: c.data.startswith('checkregister_'))
async def check_register(callback_query: types.CallbackQuery):
    current_user_telegram_id = int(callback_query.data.split('_')[1])
    await is_registered(current_user_telegram_id)
    await bot.answer_callback_query(callback_query.id)


async def is_registered(current_user_telegram_id):

    current_user = session.query(User).filter_by(telegram_id=current_user_telegram_id).first()

    if current_network == Network.MUMBAI:
        address = current_user.business_address_mumbai
        instance_contract = master_contract_mumbai.get_instance_contract(address)

        session.query(User).filter_by(telegram_id=current_user_telegram_id).update({
            "instance_contract_mumbai": instance_contract,
        })

    else:
        address = current_user.business_address_sepolia
        instance_contract = master_contract_sepolia.get_instance_contract(address)

        session.query(User).filter_by(telegram_id=current_user_telegram_id).update({
            "instance_contract_sepolia": instance_contract,
        })

    session.commit()

    await bot.send_message(
        text=f'Instance contract {instance_contract} successfully set!',
        chat_id=current_user_telegram_id,
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

    start_index = page * 5
    end_index = start_index + 5

    all_channels_to_approve = session.query(Channel).filter(Channel.is_approved == 0).all()

    if not all_channels_to_approve:
        await bot.send_message(chat_id, "No channels to approve!")
        return

    current_channels = all_channels_to_approve[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for channel in current_channels:
        button_text = f"{channel.author} - {channel.url}"
        keyboard.row(InlineKeyboardButton(text=button_text, callback_data=f'infoapprove_{channel.id}'))

    if page > 0:
        keyboard.row(InlineKeyboardButton(text="<<<", callback_data=f"prevapprove_{page}"))
    if end_index < len(all_channels_to_approve):
        keyboard.row(InlineKeyboardButton(text=">>>", callback_data=f"nextapprove_{page}"))

    await bot.send_message(chat_id, "Channels to approve list:", reply_markup=keyboard.as_markup())


async def show_channel_to_approve_info(chat_id, channel_id: int):

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Approve', callback_data=f'approve_{channel_id}'))
    keyboard.row(InlineKeyboardButton(text='Back to list', callback_data='back_to_approve_list'))

    channel = session.query(Channel).filter(Channel.id == channel_id).first()

    await bot.send_message(
        chat_id,
        text=f'Author: {channel.author}\n'
             f'URL: {channel.url}\n'
             f'Subscription cost: {channel.subscription_cost}',
        reply_markup=keyboard.as_markup()
    )


@dp.callback_query(lambda c: c.data.startswith('back_to_approve_list'))
async def callback_back_approve(callback_query: types.CallbackQuery):
    await show_channels_to_approve_page(callback_query.message.chat.id)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('infoapprove'))
async def callback_info(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[1])
    await show_channel_to_approve_info(
        channel_id=channel_id,
        chat_id=callback_query.message.chat.id,
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
    current_channel = session.query(Channel).filter_by(id=channel_id).first()

    current_user_telegram_id = current_channel.author
    current_user = session.query(User).filter_by(telegram_id=current_user_telegram_id).first()

    # try:
    #     new_instance_contract = master_contract.create_instance_contract(current_user.business_address)
    #
    #     session.query(User).filter_by(telegram_id=current_user_telegram_id).update({
    #         'instance_contract': new_instance_contract,
    #     })
    #
    # except:
    #     pass

    session.query(Channel).filter_by(id=channel_id).update({"is_approved": 1})
    session.commit()

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

    current_user = session.query(User).filter_by(telegram_id=message.chat.id).first()

    if current_network == Network.MUMBAI:
        current_business_address = current_user.business_address_mumbai
    else:
        current_business_address = current_user.business_address_sepolia

    if current_business_address is None:
        await bot.send_message(
            text='Please, set your business address, by /set_address command',
            chat_id=message.chat.id,
        )

        return

    try:
        channel_url = str(args[1])
        channel_author = str(message.from_user.id)
        channel_subscription_cost = int(args[2])
    except (IndexError, ValueError):
        await bot.send_message(
            text='Type /add_channel <url> <subscription cost>',
            chat_id=message.chat.id,
        )
        return

    new_channel = Channel(
        url=channel_url,
        author=channel_author,
        subscription_cost=channel_subscription_cost,
        is_approved=False,
    )

    session.add(new_channel)
    session.commit()

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

    start_index = page * 5
    end_index = start_index + 5
    all_channels = session.query(Channel).filter(Channel.is_approved == 1).all()

    if not all_channels:
        await bot.send_message(chat_id, "No channels to subscribe!")
        return

    current_channels = all_channels[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for channel in current_channels:
        button_text = f"{channel.author} - {channel.url}"
        keyboard.row(InlineKeyboardButton(text=button_text, callback_data=f'info_{channel.id}'))

    if start_index > 0:
        keyboard.row(InlineKeyboardButton(text="<<<", callback_data=f"prev_{page}"))
    if end_index < len(all_channels):
        keyboard.row(InlineKeyboardButton(text=">>>", callback_data=f"next_{page}"))

    await bot.send_message(chat_id, "List of channels:", reply_markup=keyboard.as_markup())


async def show_channel_info(chat_id, channel_id: int):

    keyboard = InlineKeyboardBuilder()
    channel = session.query(Channel).filter(Channel.id == channel_id).first()

    if current_network == Network.SEPOLIA:
        keyboard.row(InlineKeyboardButton(text='Subscribe with ETH (Eth)', callback_data=f'subscribe_eth_{channel_id}'))
        keyboard.row(InlineKeyboardButton(text='Subscribe with USDT (Eth)', callback_data=f'subscribe_wbtc_{channel_id}'))
    else:
        keyboard.row(InlineKeyboardButton(text='Subscribe with MATIC (Polygon)', callback_data=f'subscribe_matic_{channel_id}'))
        keyboard.row(InlineKeyboardButton(text='Subscribe with DERC (Polygon)', callback_data=f'subscribe_derc_{channel_id}'))

    keyboard.row(InlineKeyboardButton(text='Back to list', callback_data='back_to_channels_list'))

    await bot.send_message(
        chat_id,
        text=f'Info about channel:\n'
             f'URL: {channel.url}\n'
             f'Author: {channel.author}\n'
             f'Subscription cost: {channel.subscription_cost}',
        reply_markup=keyboard.as_markup(),
    )


@dp.callback_query(lambda c: c.data.startswith('subscribe'))
async def callback_subscribe(callback_query: types.CallbackQuery):

    token = str(callback_query.data.split('_')[1])
    channel_id = int(callback_query.data.split('_')[2])

    amount = int(session.query(Channel).filter_by(id=channel_id).first().subscription_cost)

    token_address = config.token_addresses[token]

    author_id = session.query(Channel).filter_by(id=channel_id).first().author

    if current_network == Network.MUMBAI:

        author_instance_contract = (session.query(User).filter_by(telegram_id=author_id)
                             .first()).instance_contract_mumbai

        instance_contract = InstanceContract(
            provider_url=config.PROVIDER_MUMBAI_URL,
            contract_address=author_instance_contract,
        )

    else:

        author_instance_contract = (session.query(User).filter_by(telegram_id=author_id)
                             .first()).instance_contract_sepolia

        instance_contract = InstanceContract(
            provider_url=config.PROVIDER_SEPOLIA_URL,
            contract_address=author_instance_contract,
        )

    escrow_contract_address = instance_contract.get_escrow_contract()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text=f'Subscribe {token.capitalize()}',
        url=f'{config.PAYMENT_SERVER}/transfer/subscribe/{author_instance_contract}/{escrow_contract_address}/{token_address}/{amount}',
    ))

    keyboard.row(InlineKeyboardButton(
        text=f'Check subscription',
        callback_data=f'checksubs_{channel_id}_{callback_query.message.chat.id}',
    ))

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f'instance_token: {author_instance_contract}\n'
             f'token_address: {token_address}',
        reply_markup=keyboard.as_markup(),
    )

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith('checksubs'))
async def callback_prev(callback_query: types.CallbackQuery):

    channel_id = int(callback_query.data.split('_')[1])
    user_id = int(callback_query.data.split('_')[2])

    new_subscription = Subscription(
        user_id=user_id,
        channel_id=channel_id,
        duration=30,
    )

    session.add(new_subscription)
    session.commit()

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f'Successfully subscribed!',
    )

    await bot.answer_callback_query(callback_query.id)


@dp.message(Command('list_channels'))
async def start_command(message: types.Message):
    await show_channels_page(message.chat.id)


@dp.callback_query(lambda c: c.data.startswith('back_to_channels_list'))
async def callback_back(callback_query: types.CallbackQuery):
    await show_channels_page(callback_query.message.chat.id)
    await bot.answer_callback_query(callback_query.id)


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


@dp.callback_query(lambda c: c.data.startswith('info'))
async def callback_info(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[1])
    await show_channel_info(callback_query.message.chat.id, channel_id=channel_id)
    await bot.answer_callback_query(callback_query.id)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

