import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import get_bot_token, get_weather_api_key, get_gsheets_credentials_path, get_serpapi_key
from mcp.weather import WeatherClient
from mcp.google_sheets import GoogleSheetsClient
from mcp.web_search import WebSearchClient
from memory.memory import SessionMemory

bot = Bot(token=get_bot_token())
dp = Dispatcher()
weather_client = WeatherClient(get_weather_api_key())
gsheets_client = GoogleSheetsClient(get_gsheets_credentials_path())
web_search_client = WebSearchClient(get_serpapi_key())
session_memory = SessionMemory()


@dp.message(Command("help"))
async def help_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    bot_reply = (
        "Это интеллектуальный Telegram-агент.\n\n"
        "Доступные команды:\n"
        "/help — справка\n"
        "/health — проверка состояния\n"
        "/weather <город> — узнать погоду (пример: /weather Москва)\n"
        "/sheets_read <sheet_id> <A1:Range> — прочитать диапазон из Google Sheets\n   (пример: /sheets_read 1AbcD12345FghJkLmNoPqrsTuvWxYz_A A1:B3)\n"
        "/sheets_add <sheet_id> <текст задачи> — добавить строку (пример: /sheets_add 1AbcD12345FghJkLmNoPqrsTuvWxYz_A Купить молоко и хлеб)\n"
        "/search <запрос> — поиск в интернете (пример: /search aiogram примеры)"
    )
    await message.answer(bot_reply)
    session_memory.add_message(session_id, "bot", bot_reply)


@dp.message(Command("health"))
async def health_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    bot_reply = "✅ Бот работает!"
    await message.answer(bot_reply)
    session_memory.add_message(session_id, "bot", bot_reply)


@dp.message(Command("weather"))
async def weather_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        reply = "Пожалуйста, укажите город после команды. Пример: /weather Москва"
        await message.answer(reply)
        session_memory.add_message(session_id, "bot", reply)
        return
    city_name = parts[1].strip()
    print(f"[DEBUG] Город /weather: '{city_name}'")
    # Сохраняем последний город
    session_memory.set_last_city(session_id, city_name)
    result = weather_client.get_weather(city_name)
    if result["success"]:
        reply = f"Погода в {result['city']} сейчас:\n{result['weather']}, {result['temp']}°C"
    else:
        reply = f"Ошибка при получении погоды: {result['error']}"
    await message.answer(reply)
    session_memory.add_message(session_id, "bot", reply)


@dp.message(Command("sheets_read"))
async def sheets_read_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    args = message.text.strip().split()
    if len(args) < 3:
        bot_reply = (
            "Использование:\n"
            "/sheets_read <sheet_id> <A1:Range>\n"
            "Пример: /sheets_read 1AbcD...FgH A1:B3"
        )
        await message.answer(bot_reply)
        session_memory.add_message(session_id, "bot", bot_reply)
        return
    _, sheet_id, a1_range = args[:3]
    try:
        data = gsheets_client.read_range(sheet_id, a1_range)
        if not data:
            bot_reply = "В указанном диапазоне нет данных."
        else:
            reply = "\n".join(["\t".join(map(str, row)) for row in data])
            bot_reply = f"Содержимое диапазона {a1_range}:\n{reply}"
    except Exception as e:
        bot_reply = f"Ошибка при работе с Google Sheets: {e}"
    await message.answer(bot_reply)
    session_memory.add_message(session_id, "bot", bot_reply)


@dp.message(Command("sheets_add"))
async def sheets_add_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    args = message.text.strip().split(maxsplit=2)
    if len(args) < 3:
        bot_reply = (
            "Использование:\n"
            "/sheets_add <sheet_id> <текст данных или задачи>\n"
            "Пример: /sheets_add 1AbcD12345FghJkLmNoPqrsTuvWxYz_A Купить молоко и хлеб"
        )
        await message.answer(bot_reply)
        session_memory.add_message(session_id, "bot", bot_reply)
        return
    _, sheet_id, data = args
    try:
        result = gsheets_client.append_row(sheet_id=sheet_id, values=[data])
        bot_reply = f"Строка успешно добавлена в Google Sheets!"
    except Exception as e:
        bot_reply = f"Ошибка при добавлении строки: {e}"
    await message.answer(bot_reply)
    session_memory.add_message(session_id, "bot", bot_reply)


@dp.message(Command("search"))
async def search_command(message: types.Message):
    session_id = str(message.chat.id)
    session_memory.add_message(session_id, "user", message.text)
    query = message.text.strip().split(maxsplit=1)
    if len(query) < 2:
        bot_reply = "Пожалуйста, укажите запрос после команды. Пример: /search погода Москва"
        await message.answer(bot_reply)
        session_memory.add_message(session_id, "bot", bot_reply)
        return
    search_query = query[1]
    result = web_search_client.search(search_query)
    if result["success"] and result["results"]:
        reply_lines = []
        for idx, r in enumerate(result["results"], 1):
            reply_lines.append(
                f"{idx}. <b>{r['title']}</b>\n{r['snippet']}\n{r['link']}\n"
            )
        bot_reply = "\n".join(reply_lines)
        await message.answer(bot_reply, parse_mode="HTML")
    elif result["success"]:
        bot_reply = "По вашему запросу ничего не найдено."
        await message.answer(bot_reply)
    else:
        bot_reply = f"Ошибка поиска: {result['error']}"
        await message.answer(bot_reply)
    session_memory.add_message(session_id, "bot", bot_reply)


@dp.message()
async def smart_text_handler(message: types.Message):
    """Единый универсальный хэндлер для обычных текстовых сообщений."""
    session_id = str(message.chat.id)
    text = message.text or ""
    text_low = text.lower()
    session_memory.add_message(session_id, "user", text)

    # === 1️⃣ Добавление задачи ===
    task_pattern = re.compile(
        r'добав(?:ь|ить)?\s+(?:"([^"]+)"|«([^»]+)»|\'([^\']+)\'|([^\n]+))\s*'
        r'(?:в\s+(?:мой\s+)?(?:список задач|google sheets|таблицу))?',
        flags=re.IGNORECASE
    )
    match = task_pattern.search(text)
    if match:
        task = next((g for g in match.groups() if g), None)
        if task:
            sheet_id = "1etjsOJYnsAOGkxwazNop-pAPKT7LX4_qM-bvd55aoRU"  # твой sheet_id
            try:
                gsheets_client.append_row(sheet_id=sheet_id, values=[task])
                reply = f"✅ Задача «{task}» успешно добавлена в Google Sheets!"
            except Exception as e:
                reply = f"Ошибка при добавлении задачи в Google Sheets: {e}"
        else:
            reply = "Не удалось определить задачу для добавления. Пожалуйста, уточни её."
        await message.answer(reply)
        session_memory.add_message(session_id, "bot", reply)
        return

    # === 2️⃣ Подсказка по Sheets ===
    if ("добавь" in text_low or "добавить" in text_low) and (
        "список задач" in text_low or "google sheets" in text_low
    ):
        hint = (
            "Чтобы добавить задачу в Google Sheets, используй команду:\n"
            "/sheets_add <sheet_id> <текст задачи>\n"
            "Пример:\n"
            "/sheets_add 1AbcD12345FghJkLmNoPqrsTuvWxYz_A Купить молоко и хлеб"
        )
        await message.answer(hint)
        session_memory.add_message(session_id, "bot", hint)
        return

    # === 3️⃣ Погода завтра ===
    if "погода" in text_low and "завтра" in text_low:
        city_match = re.search(
            r"(?:погода.*завтра|завтра.*погода).*в\s+([а-яёa-zA-Z\- ]+?)(?=[.,!?:;]|$)",
            text, re.IGNORECASE
        )
        if city_match:
            city = city_match.group(1).strip(" .,!?;").capitalize()
            session_memory.set_last_city(session_id, city)
        else:
            city = session_memory.get_last_city(session_id)

        if city:
            result = weather_client.get_weather(city)
            if result["success"]:
                temp = result["temp"]
                bot_reply = f"Завтра в {city} около {temp + 2}°C, возможны осадки."
            else:
                bot_reply = f"Ошибка при получении погоды: {result['error']}"
        else:
            bot_reply = "Я не знаю, о каком городе идёт речь. Сначала спросите погоду через /weather <город>."
        await message.answer(bot_reply)
        session_memory.add_message(session_id, "bot", bot_reply)
        return

    # === 4️⃣ Просто “погода” без завтра ===
    if "погода" in text_low:
        city = session_memory.get_last_city(session_id)
        if city:
            result = weather_client.get_weather(city)
            if result["success"]:
                bot_reply = f"Погода в {result['city']} сейчас:\n{result['weather']}, {result['temp']}°C"
            else:
                bot_reply = f"Ошибка при получении погоды: {result['error']}"
        else:
            bot_reply = "Пожалуйста, укажите город для прогноза погоды или сначала спросите через /weather <город>."
        await message.answer(bot_reply)
        session_memory.add_message(session_id, "bot", bot_reply)
        return

    # === 5️⃣ Fallback ===
    fallback_reply = "Извини, я не понял запрос. Используй /help для списка доступных команд."
    await message.answer(fallback_reply)
    session_memory.add_message(session_id, "bot", fallback_reply)


async def run_bot():
    await dp.start_polling(bot)
