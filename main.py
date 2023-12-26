import random

import db
import os
# from config_reader import config
from aiogram import Bot, types
# Память для машины состояний и машина состояний
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
# Машина состояний импорты
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor


storage = MemoryStorage()


class Register(StatesGroup):
    start = State()
    enter_fullname = State()
    choose_car = State()
    match = State()


# Создаём бота исходя из полученного токена
bot = Bot(token="6631204524:AAEDWHlQrngDBkEDWYNwSlG60KzET0WPXWA")
dp = Dispatcher(bot, storage=storage)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton(text='ПОЕХАЛИ🚀'))

cars_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    KeyboardButton(text='TANK300'), KeyboardButton(text='TANK500'))

actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton(text='Сменить тему для разговора')).add(KeyboardButton(text='Подобрать нового собеседника'))


# Обработка команды /start
@dp.message_handler(commands='start', state='*')
async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    check_flag = await db.check_user(message.from_user.id, message.from_user.username)
    if not check_flag:
        await bot.send_message(message.from_user.id, "Привет!\n\n"
                                                     "Я бот, который поможет обрести новые знакомства"
                                                     " и найти интересных людей для общения на мероприятии"
                                                     " в честь годовщины бренда TANK в России.\n\n"
                                                     "Чтобы найти собеседника, нужно ответить на два моих вопроса."
                                                     " Готов?",
                               reply_markup=main_keyboard)
        await Register.start.set()


# Обработка команды состояния Register.start
@dp.message_handler(state=Register.start)
async def command_start(message: types.Message, state: FSMContext):
    if "ПОЕХАЛИ" in message.text:
        await bot.send_message(message.from_user.id, "Как тебя зовут? Напиши имя и фамилию.")
        await Register.enter_fullname.set()

    else:
        await bot.send_message(message.from_user.id, "Хмм.. Дайте немного подумать🤔\n\n"
                                                     "К сожалению, я пока что не могу дать ответ на ваш вопрос,"
                                                     " но вы можете обратиться за помощью к организатору или к хостес"
                                                     " на стойку ресепшн.")


# Обработка команды состояния Register.start
@dp.message_handler(state=Register.enter_fullname)
async def command_start(message: types.Message, state: FSMContext):
    media = types.MediaGroup()
    media.attach_photo(types.InputMediaPhoto(open("TANK300.png", 'rb'),
                                             caption=f"Теперь выбери свой автомобиль TANK"))
    media.attach_photo(types.InputMediaPhoto(open("TANK500.png", 'rb')))

    await bot.send_message(message.from_user.id, f"Приятно познакомиться, {message.text}",
                           reply_markup=cars_keyboard)

    await bot.send_media_group(message.from_user.id, media)

    await db.update_column_in_users_forms(message.text, "fullname", message.from_user.id)
    await Register.choose_car.set()


# Обработка названия автомобиля
@dp.message_handler(state=Register.choose_car)
async def command_start(message: types.Message, state: FSMContext):
    if "TANK300" in message.text or "TANK500" in message.text:
        await bot.send_message(message.from_user.id, "Я уже начал подбирать собеседника, с которым вы вместе"
                                                     " сможете попробовать авторские коктейли от TANK.\n"
                                                     "Не отключайте уведомления и ознакомьтесь с"
                                                     " инструкцией на картинке:")
        await db.update_column_in_users_forms(message.text, "car", message.from_user.id)
        await db.update_column_in_users_forms('false', "match_flag", message.from_user.id)
        user_id, res_user = await db.select_user_from_users_forms_with_match(message.from_user.id)
        user_tg_id = await db.select_tg_id(user_id)

        if res_user != 0:
            await bot.send_message(message.from_user.id,
                                   f"Случился мэтч! С помощью алгоритма я нашел для тебя собеседника🪄\n\n"
                                   f"Его имя: {res_user}\n\n"
                                   f"Через 5 минут вы встречаетесь в зоне коктейльного бара,"
                                   f" опознать своего нового знакомого сможешь по бейджику\n\n"
                                   f"Если возникнут трудности, ты всегда можешь обратиться к организатору "
                                   f"или на стойку ресепшн к хостес за помощью.")

            themes = await db.select_themes(message.from_user.id)

            random_theme = themes[0][random.randint(0, len(themes[0])-1)]
            print(f"random_theme {random_theme}")
            msg = ''

            if random_theme == "Путешествия":
                msg = "Для каждой созданной мною пары для знакомства я предлагаю тему для общения 💭\n" \
                      "Ваша тема - Путешествия!)\n\n" \
                      "Расскажите, какие интересные места вы посетили на своем автомобиле TANK\n\n" \
                      "И куда бы отправились в путешествие прямо сейчас\n\n" \
                      "Греться на теплом песочке у моря или покорять горные вершины на лыжах? Что больше тебе по душе?"

            elif random_theme == "Еда":
                msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                       "Ваша тема -  Еда.\n\n"
                       "Обсудите свои любимые блюда и рестораны,"
                       " посоветуйте собеседнику классные места в городе и за его пределами.\n\n"
                       "Кстати, кухня какого народа мира вам больше всего по душе?")

            elif random_theme == "Работа и карьера":
                msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                       "Ваша тема - Работа и карьера.\n\n"
                       "Сообщество TANK - это про полезные и интересные знакомства,"
                       " в том числе для работы. Расскажи, чем ты занимаешься?")

            elif random_theme == "Досуг в Москве":
                msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                       "Ваша тема - Досуг в Москве.\n\n"
                       "Расскажите собеседнику о своих любимых местах в городе."
                       " Куда ты предпочитаешь отправиться вместе с семьей или друзьями в выходные? ")

            elif random_theme == "Спорт и увлечения":
                msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                       "Ваша тема - Спорт и увлечения.\n\n"
                       "Если бы я был человеком, то попробовал бы всё от "
                       "волейбола до кёрлинга. Кажется, мне больше нравятся командные игры.\n\n"
                       "А у тебя есть спортивные увлечения? ")

            new_themes = themes[0]
            print(f"new_themes {new_themes}")
            new_themes.remove(random_theme)
            print(f"new_themes {new_themes}")
            await bot.send_message(message.from_user.id, msg, reply_markup=actions_keyboard)

            name = await db.select_fullname(message.from_user.id)

            await bot.send_message(user_tg_id,
                                   f"Случился мэтч! С помощью алгоритма я нашел для тебя собеседника🪄\n\n"
                                   f"Его имя: {name}\n\n"
                                   f"Через 5 минут вы встречаетесь в зоне коктейльного бара,"
                                   f" опознать своего нового знакомого сможешь по бейджику\n\n"
                                   f"Если возникнут трудности, ты всегда можешь обратиться к организатору "
                                   f"или на стойку ресепшн к хостес за помощью.")
            await bot.send_message(user_tg_id, msg)
            await db.update_themes(message.from_user.id, new_themes)
            await Register.match.set()

        else:
            pass

    else:
        await bot.send_message(message.from_user.id, "Пожалуйста, выберите один из пунктов с клавиатуры",
                               reply_markup=cars_keyboard)


@dp.message_handler(state=Register.match)
async def command_start(message: types.Message, state: FSMContext):
    if message.text == "Сменить тему для разговора":
        themes = await db.select_themes(message.from_user.id)
        print(themes)
        random_theme = themes[0][random.randint(0, len(themes[0]) - 1)]
        print(random_theme)
        msg = ''

        if random_theme == "Путешествия":
            msg = "Для каждой созданной мною пары для знакомства я предлагаю тему для общения 💭\n" \
                  "Ваша тема - Путешествия!)\n\n" \
                  "Расскажите, какие интересные места вы посетили на своем автомобиле TANK\n\n" \
                  "И куда бы отправились в путешествие прямо сейчас\n\n" \
                  "Греться на теплом песочке у моря или покорять горные вершины на лыжах? Что больше тебе по душе?"

        elif random_theme == "Еда":
            msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                   "Ваша тема -  Еда.\n\n"
                   "Обсудите свои любимые блюда и рестораны,"
                   " посоветуйте собеседнику классные места в городе и за его пределами.\n\n"
                   "Кстати, кухня какого народа мира вам больше всего по душе?")

        elif random_theme == "Работа и карьера":
            msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                   "Ваша тема - Работа и карьера.\n\n"
                   "Сообщество TANK - это про полезные и интересные знакомства,"
                   " в том числе для работы. Расскажи, чем ты занимаешься?")

        elif random_theme == "Досуг в Москве":
            msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                   "Ваша тема - Досуг в Москве.\n\n"
                   "Расскажите собеседнику о своих любимых местах в городе."
                   " Куда ты предпочитаешь отправиться вместе с семьей или друзьями в выходные? ")

        elif random_theme == "Спорт и увлечения":
            msg = ("Для каждой созданной мною пары для знакомства я предлагаю тему для общения💭\n\n"
                   "Ваша тема - Спорт и увлечения.\n\n"
                   "Если бы я был человеком, то попробовал бы всё от "
                   "волейбола до кёрлинга. Кажется, мне больше нравятся командные игры.\n\n"
                   "А у тебя есть спортивные увлечения? ")

        new_themes = themes[0]
        print(new_themes)
        new_themes.remove(random_theme)
        print(new_themes)
        await db.update_themes(message.from_user.id, new_themes)
        await bot.send_message(message.from_user.id, msg, reply_markup=actions_keyboard)

    elif message.text == "Подобрать нового собеседника":
        await bot.send_message(message.from_user.id, "В разработке")

    else:
        await bot.send_message(message.from_user.id, "Уверен, вам с собеседником будет интересно это обсудить🙌🏻\n"
                                                     "Возможно ваш собеседник уже ждет тебя у барной стойки."
                                                     " Желаю классно провести время!")

executor.start_polling(dp, skip_updates=True)
