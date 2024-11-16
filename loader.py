from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TOKEN
from handlers.commands import fetch_and_display_data, run_tests, start, history, custom, help_command, unknown_command
from database.models import database

def setup_dispatcher(application: Application) -> None:
    """
    Настройка диспетчера команд для приложения.

    :param application: Экземпляр приложения Telegram
    """
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('test', run_tests))
    application.add_handler(CommandHandler(['low', 'high'], fetch_and_display_data))
    application.add_handler(CommandHandler('history', history))
    application.add_handler(CommandHandler('custom', custom))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))  # Обработка неизвестных команд

def main() -> None:
    """
    Основная функция для запуска бота.
    """
    application = Application.builder().token(TOKEN).build()

    # Инициализация базы данных
    database.connect()
    database.create_tables([], safe=True)  # Обновление таблиц по мере необходимости
    database.close()

    setup_dispatcher(application)
    application.run_polling()

if __name__ == "__main__":
    main()
