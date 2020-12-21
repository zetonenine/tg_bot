#!/usr/bin/python3.3

import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from bottle import run, post


# import sqlite3
from main.sqlighter import SQLighter
from main.messages import MESSAGES
from main.utils import TestStates


# logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

db = SQLighter('tables.db')


@dp.message_handler(commands=['start'], state='*')
async def start_and_add_user_in_BD(message: types.Message):

    """Начало работы бота и добавление юзера в БД.
    Возможно стоит добавлять в БД на следующих этапах"""

    await TestStates.default_process.set()

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    await message.answer(MESSAGES['start'])


@dp.message_handler(commands=['help'], state='*')
async def help_message(message: types.Message):
    """Информация о самом боте"""
    await message.reply(MESSAGES['help'])


@dp.message_handler(commands=['howto'], state='*')
async def help_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.reply(MESSAGES['howto'])


# ХЭНДЛЕРЫ ОБРАБОТЧИКИ ЧАТА - СОСТОЯНИЕ chat_process


@dp.message_handler(state=TestStates.default_process, commands=['find'])
async def finding(message: types.Message, state: FSMContext):

    """Меняет status юзера на '1' или 'True'.
    Если юзер не будет добавлен в БД ранее
    то нужно вызвать db.add_user"""

    if db.user_exists(message.from_user.id):
        db.status_true(True, message.from_user.id)
        await message.answer('Ищем собеседника..')
        await state.finish()
        await TestStates.chat_process.set()
        """Ищем свободного юзера со status'ом = 1. Добавляем юзера в состояние."""

        partner_chatID = db.finding_free_chat(message.from_user.id, None)
        if partner_chatID is not None:
            await message.answer(f'Собеседник найден. Напишите ему :)')
            await bot.send_message(partner_chatID, 'Собеседник найден, кто же напишет первым? :)')
        # else:
            # await message.answer('Нет свободных собеседников, попробуйте снова /chat')


@dp.message_handler(content_types=['voice'], state=TestStates.chat_process)
async def voice_messages_resender(message: types.voice, state: FSMContext):

    """Обработчик войсов, пересылка сообщения если чат установлен, и ответ, если чата нет"""

    pcID = db.pcID_checker(message.from_user.id)
    await bot.send_voice(pcID, message.voice.file_id)


@dp.message_handler(content_types=['text', 'sticker', 'photo'], state=TestStates.chat_process)
async def messages_resender(message: types.Message, state: FSMContext):
    pcID = db.pcID_checker(message.from_user.id)

    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""
    if message.text != '/stop':
        if message.text != '/find':
            await message.answer('Запишите голосовое сообщение')
        else:
            await message.answer('Поиск уже запущен')
    else:
        await stop_chat(message, state)


@dp.message_handler(commands=['stop'], state=TestStates.chat_process)
async def stop_chat(message: types.Message, state: FSMContext):

    """Меняет status на '0' или 'False'.
    Также очищает partner_chatID.
    Как и в функции finding, возможно нужен вызов db.add_user"""

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    pcID = db.status_false_and_clear_partner(False, message.from_user.id, None)
    await state.finish()
    await TestStates.default_process.set()
    await message.answer('Диалог окончен..')
    await bot.send_message(pcID, 'Диалог окончен..')


# ЗДЕСЬ ЗАКАНЧИВАЮТСЯ


@dp.message_handler(commands=['check'], state=TestStates.default_process)
async def checking(message: types.Message):

    """Проверка на наличие юзера в базе данных"""

    if not db.user_exists(message.from_user.id):
        await message.answer('Вы не в базе')
    else:
        await message.answer('Вы в базе')


@dp.message_handler(commands=['delete'], state=TestStates.default_process)
async def deleting(message: types.Message):

    """Удаление юзера из БД"""

    if db.user_exists(message.from_user.id):
        db.user_deleting(message.from_user.id)
        await message.answer('Вы удалены из базы')


@dp.message_handler(state=TestStates.default_process, content_types=types.ContentTypes.ANY)
async def messages_resender(message: types.Message):
    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""

    if message.content_type == 'voice':
        await message.answer('Для начала вам нужно найти собеседника. Чтобы это сделать введите команду /find')
        # await bot.send_message(pcID, message)
    else:
        await message.answer('Это классно конечно, но не то. Чтобы найти собеседника, введите команду /find')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, timeout=60)
    run(host='localhost', port=8080, debug=True)


