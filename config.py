import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:oquojdar21@localhost/ecommerce')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Cache
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = REDIS_URL