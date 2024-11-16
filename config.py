import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/requests.db')
