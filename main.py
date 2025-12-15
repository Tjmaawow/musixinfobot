import asyncio
import uuid

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import imagen
import infoparser
import userauthorizer

BOT_TOK = "Токен в BotFather"
DEV_ID = "Айди разработчика"

bot = Bot(token=BOT_TOK)
dp = Dispatcher()
imgen = imagen.Imagen()
infopars = infoparser.MusicInfoParser()
userauth = userauthorizer.Authorizer()


@dp.inline_query()
async def inline_handler(query: types.InlineQuery):
    res = userauth.checkAuth(query.from_user.id)
    if res == 0:
        return await query.answer(
            [
                types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Ты не авторизован.",
                    description="Перейди в чат со мной и введи /start.",
                    input_message_content=types.InputTextMessageContent(
                        message_text='Ехали два парня гея в маршрутке. Один другому говорит - "Слышь, а давай прям тут?" А тот отвечает "Ты что! Тут же люди!". "Да никто на тебя не смотрит! Вот смотри." и спрашивает на всю маршрутку "Люди добрые, сколько время?" Все молчат. Ну и поебались они прям в маршрутке. Тут на конечной все уже вышли. Водитель выходит в салон, смотрит - на задних рядах сидит дедушка, за сердце держась. - "Дедушка, дедушка, что с вами? Вам плохо? Чего ж вы валерьянки не попросили у кого?", но дед ему отвечает: "Да я, сынок, зассал! Тут один спросил сколько время, так его в очко выебали". Кстати, пользователь не авторизован'
                    ),
                )
            ],
            cache_time=0,
        )
    platform = res[0]
    platformId = res[1]
    text = query.query.strip()
    if text == "file":
        result = types.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Пока что не поддерживаю.",
            descriprion="Ты от меня уже mp3 хочешь? а не дохуя ли?",
            input_message_content=types.InputTextMessageContent(message_text="ого"),
        )
        await query.answer([result], cache_time=0)
    else:
        if platform == "Spotify":
            res = await infopars.getInfoAboutNow_spotify(platformId)
        elif platform == "Яндекс музыка":
            res = await infopars.getInfoAboutNow_YM(platformId)
        else:
            result = types.InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Пока что не поддерживаю.",
                descriprion="Разработчик рукожоп.",
                input_message_content=types.InputTextMessageContent(
                    message_text="Разработчик рукожоп кстати"
                ),
            )
            return await query.answer([result], cache_time=0)
        if isinstance(res, int):
            if res == 200:
                result = types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Ничего не воспроизводится(",
                    description="А возможно у тебя это скрыто в настройках площадки...",
                    input_message_content=types.InputTextMessageContent(
                        message_text="Юзер ничего не слушает"
                    ),
                )
            else:
                result = types.InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Ошибка. Прости(",
                    description=f"Код ошибки {res}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"Ошибка {res}"
                    ),
                )
            await query.answer([result], cache_time=0)
        else:
            imag = await imgen.genNew(
                res["title"], ", ".join(res["artists"]), res["thumb"]
            )
            msg = await bot.send_photo(
                chat_id=-1003482141253,
                photo=BufferedInputFile(imag.read(), filename="track.png"),
                disable_notification=True,
            )
            file_id = msg.photo[-1].file_id
            result = types.InlineQueryResultCachedPhoto(
                id=str(uuid.uuid4()),
                title=res["title"],
                description=", ".join(res["artists"]),
                photo_file_id=file_id,
                caption=f"<a href='{res['url']}'>{platform}</a> || <a href='{res['all_url']}'>Все сервисы</a>",
                parse_mode="HTML",
            )
            await query.answer([result], cache_time=0)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("""
Привет! Я Musix Bot, или же @musixinfobot 🙌
Используй меня для того чтобы поделиться треком, который ты слушаешь прямо сейчас. 💕
Площадки которые я поддерживаю: Spotify 💚, Яндекс музыка💛
Как использовать? Есть два способа поделиться:
1. Отправить ему название трека, автора трека и превью
- Я делаю это автоматически, в красивом виде
- Твой друг переходит по ссылке(которую я прилагаю) на свой сервис и слушает там
- Использование: `@musixinfobot` в других чатах
2. Отправить ему mp3 файл
- Я делаю это тоже автоматически, но уже без красоты
- Твой друг слушает трек прямо из Telegram
- Использование: `@musixinfobot file` в других чатах

Для начала введи /auth
Надеюсь, ты останешься доволен мной)
    """)


@dp.message(Command("checkme"))
async def check_handler(message: types.Message):
    res = userauth.checkAuth(message.from_user.id)
    if res != 0:
        await message.answer(f"Ты авторизован. Площадка - {res[0]}")
    else:
        await message.answer("Ты еще не авторизован. Для начала введи /auth")


class AuthState(StatesGroup):
    choosing_platform = State()  # Шаг 1: Ждем выбор кнопки
    waiting_for_input = State()  # Шаг 2: Ждем текст от пользователя


@dp.message(Command("auth"))
async def auth_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Для начала, выбери площадку) 🙌",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Spotify")],
                [KeyboardButton(text="Яндекс музыка")],
                [KeyboardButton(text="Отмена.")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    await state.set_state(AuthState.choosing_platform)


@dp.message(AuthState.choosing_platform, F.text.lower() == "отмена.")
@dp.message(AuthState.waiting_for_input, F.text.lower() == "отмена.")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Хорошо, значит мы так и не познакомимся(", reply_markup=ReplyKeyboardRemove()
    )


@dp.message(AuthState.choosing_platform)
async def platform_choosing(message: types.Message, state: FSMContext):
    platform = message.text
    if platform not in ["Spotify", "Яндекс музыка"]:
        await message.answer(
            "Выбери площадку кнопками, бро)\nЕсли твоей площадки там нет, то увы и ах, я ее не поддерживаю."
        )
    else:
        await state.update_data(platform=platform)

        if platform == "Spotify":
            text = """
Инструкция по авторизации на спотике🙌
1. Зайди на сайт <a href='https://stats.fm/'>stats.fm</a>
2. Войди в аккаунт при помощи аккаунта Spotify
3. Перейди в настройки аккаунта
4. В месте "Custom Url" скопируй все что после stats.fm/
5. Отправь мне
"""
        if platform == "Яндекс музыка":
            text = """
Инструкция по авторизации на Яндекс музыке🙌
1. Открой <a href='https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d'>ссылку</a>
2. Возможно, потребуется авторизация в Яндекс ID
3. Тебя переведет на Яндекс музыку. Обрати внимание на адресную строку:
    https://music.yandex.ru/#access_token=блабла&token_type=bearer...
Все что после access_token= до &token_type - твой токен. Скопируй его и отправь мне.
p.s. Учти, что токен - вещь, которую надо держать в секрете. Имея токен, человек может получить твой номер телефона, паспортные данные, управлять воспроизведением и т.д.
p.s. Я этим не занимаюсь. Мой код открыт, если разбираешься, можешь проверить.
"""
        else:
            text = "Бляздец"

        await message.answer(
            text, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML"
        )
        await state.set_state(AuthState.waiting_for_input)


@dp.message(AuthState.waiting_for_input)
async def waiting_for_input(message: types.Message, state: FSMContext):
    platformId = message.text

    state_data = await state.get_data()
    platform = state_data.get("platform")

    userauth.createAuth(message.from_user.id, str(platform), str(platformId))

    await message.answer(
        "Супер) Запомнил, теперь можешь пользоваться мной в чатах.\nЕсли захочешь чтобы я забыл твою авторизацию, введи /unauth"
    )
    await state.clear()


@dp.message(Command("unauth"))
async def unauth_handler(message: types.Message):
    userauth.removeAllAuths(message.from_user.id)
    await message.answer("Удалил из базы данных все записи, связанные с тобой.")


async def boot():
    await dp.start_polling(bot)


asyncio.run(boot())
