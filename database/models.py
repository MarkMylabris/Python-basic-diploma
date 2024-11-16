from peewee import SqliteDatabase, Model, CharField, DateTimeField
import os

# Указываем путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), 'requests.db')
database = SqliteDatabase(db_path)

class UserRequest(Model):
    """
    Модель для хранения запросов пользователей.
    """
    username: CharField = CharField()
    command: CharField = CharField()
    data_choice: CharField = CharField(null=True)
    filter_choice: CharField = CharField()
    amount: CharField = CharField()
    name: CharField = CharField()
    timestamp: DateTimeField = DateTimeField()

    class Meta:
        database = database

def initialize_database() -> None:
    """
    Инициализировать базу данных и создать таблицы.
    """
    with database:
        database.create_tables([UserRequest])
