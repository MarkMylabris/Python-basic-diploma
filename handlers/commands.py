from telegram import Update
from telegram.ext import CallbackContext
from api.scryfall import fetch_data
from database.models import UserRequest
from utils.helpers import format_data, parse_command, parse_custom_command
from typing import List

async def start(update: Update, context: CallbackContext) -> None:
    """
    Начальное приветствие бота.
    """
    await update.message.reply_text("Привет! Я бот Scryfall. Вы можете использовать команды, например, /low или /high, чтобы искать цены на карты.")

async def run_tests(update: Update, context: CallbackContext) -> None:
    """
    Тестовые команды для проверки работы бота.
    """
    test_commands = [
        "/low card 3 Black Lotus",
        "/high card 5 Island",
        "/low set 2 Limited Edition Alpha",
        "/high set 10 Battle for Zendikar"
    ]
    for command in test_commands:
        await update.message.reply_text(f"Выполняется: {command}")
        data_choice, filter_choice, amount, name = parse_command(command)
        if data_choice and filter_choice and amount and name:
            cards = fetch_data(data_choice, filter_choice, amount, name)
            if cards:
                formatted_data = format_data(cards)
                await update.message.reply_text(formatted_data, parse_mode='Markdown')
            else:
                await update.message.reply_text("Карты не найдены.")
        else:
            await update.message.reply_text("Неверный формат команды.")

async def fetch_and_display_data(update: Update, context: CallbackContext) -> None:
    """
    Получить и отобразить данные карт.
    """
    command = update.message.text
    data_choice, filter_choice, amount, name = parse_command(command)
    if not data_choice or not filter_choice or not amount or not name:
        await update.message.reply_text("Неверный формат команды. Используйте формат: /low|high card|set число имя")
        return
    try:
        cards = fetch_data(data_choice, filter_choice, amount, name)
        if not cards:
            await update.message.reply_text("Карты не найдены.")
            return
        formatted_data = format_data(cards)
        await update.message.reply_text(formatted_data, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def history(update: Update, context: CallbackContext) -> None:
    """
    Показать историю команд пользователя.
    """
    username = update.message.from_user.username
    requests = UserRequest.select().where(UserRequest.username == username).order_by(UserRequest.timestamp.desc())
    if not requests:
        await update.message.reply_text("История запросов отсутствует.")
        return

    history_message = "История ваших запросов:\n"
    for request in requests:
        history_message += f"{request.timestamp}: {request.command} {request.filter_choice} {request.amount} {request.name}\n"
    await update.message.reply_text(history_message)

async def custom(update: Update, context: CallbackContext) -> None:
    """
    Обработка пользовательских команд с ценовым диапазоном.
    """
    command = update.message.text
    filter_choice, low_price, high_price, name = parse_custom_command(command)
    if not filter_choice or low_price is None or high_price is None or not name:
        await update.message.reply_text("Неверный формат команды. Используйте формат: /custom card|set нижняя_цена верхняя_цена имя")
        return
    try:
        cards = fetch_data(None, filter_choice, 0, name, low_price, high_price)
        if not cards:
            await update.message.reply_text("Карты не найдены в указанном диапазоне цен.")
            return
        formatted_data = format_data(cards)
        await update.message.reply_text(formatted_data, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def help_command(update: Update, context: CallbackContext) -> None:
    """
    Отображение доступных команд.
    """
    help_text = (
        "*Доступные команды:*\n"
        "/start - Начало работы с ботом\n"
        "/low card <число> <имя> - Низшие цены на карты\n"
        "/high card <число> <имя> - Высшие цены на карты\n"
        "/low set <число> <имя набора> - Низшие цены на карты из набора\n"
        "/high set <число> <имя набора> - Высшие цены на карты из набора\n"
        "/custom card <нижняя цена> <верхняя цена> <имя> - Карты в указанном диапазоне цен\n"
        "/custom set <нижняя цена> <верхняя цена> <имя набора> - Карты из набора в указанном диапазоне цен\n"
        "/history - История ваших запросов\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def unknown_command(update: Update, context: CallbackContext) -> None:
    """
    Обработка неизвестных команд.
    """
    await update.message.reply_text(
        "Извините, я не понял эту команду. Введите /help для списка доступных команд."
    )
