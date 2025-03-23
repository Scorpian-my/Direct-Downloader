from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Session Configuration
    SESSIONS_DIR = os.path.join("src", "sessions")
    TELEGRAM_SESSION = os.path.join(SESSIONS_DIR, "my_bot.session")
    INSTAGRAM_SESSION = os.path.join(SESSIONS_DIR, "Direct_TDL.json")

    # Telegram Configuration
    TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID', '********')
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '********')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '********')

    # Instagram Configuration
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '********')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '********')
    INSTAGRAM_PROXY = os.getenv('INSTAGRAM_PROXY', '')

    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')

    # Admin Configuration
    ADMIN_ID = os.getenv('ADMIN_ID', '********')

    # Rate Limiting Configuration
    TELEGRAM_RATE_LIMIT = int(os.getenv('TELEGRAM_RATE_LIMIT', '30'))
    TELEGRAM_RATE_WINDOW = int(os.getenv('TELEGRAM_RATE_WINDOW', '60'))
    INSTAGRAM_RATE_LIMIT = int(os.getenv('INSTAGRAM_RATE_LIMIT', '20'))
    INSTAGRAM_RATE_WINDOW = int(os.getenv('INSTAGRAM_RATE_WINDOW', '60'))

    # Cache Configuration
    MESSAGE_CACHE_TTL = int(os.getenv('MESSAGE_CACHE_TTL', '3600'))
    USER_CACHE_TTL = int(os.getenv('USER_CACHE_TTL', '7200'))
    MESSAGE_CACHE_SIZE = int(os.getenv('MESSAGE_CACHE_SIZE', '1000'))
    USER_CACHE_SIZE = int(os.getenv('USER_CACHE_SIZE', '500'))

    # Download Configuration
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
    MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', '52428800'))  # 50MB in bytes

    @classmethod
    def get_telegram_config(cls) -> Dict[str, Any]:
        """Get Telegram configuration"""
        return {
            "api_id": cls.TELEGRAM_API_ID,
            "api_hash": cls.TELEGRAM_API_HASH,
            "bot_token": cls.TELEGRAM_BOT_TOKEN,
            "session_file": cls.TELEGRAM_SESSION
        }

    @classmethod
    def get_instagram_config(cls) -> Dict[str, Any]:
        """Get Instagram configuration"""
        return {
            "username": cls.INSTAGRAM_USERNAME,
            "password": cls.INSTAGRAM_PASSWORD,
            "session_file": cls.INSTAGRAM_SESSION,
            "proxy": cls.INSTAGRAM_PROXY
        }

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "telegram": {
                "max_requests": cls.TELEGRAM_RATE_LIMIT,
                "time_window": cls.TELEGRAM_RATE_WINDOW
            },
            "instagram": {
                "max_requests": cls.INSTAGRAM_RATE_LIMIT,
                "time_window": cls.INSTAGRAM_RATE_WINDOW
            }
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            "message": {
                "ttl": cls.MESSAGE_CACHE_TTL,
                "maxsize": cls.MESSAGE_CACHE_SIZE
            },
            "user": {
                "ttl": cls.USER_CACHE_TTL,
                "maxsize": cls.USER_CACHE_SIZE
            }
        }

    @classmethod
    def get_download_config(cls) -> Dict[str, Any]:
        """Get download configuration"""
        return {
            "download_dir": cls.DOWNLOAD_DIR,
            "max_size": cls.MAX_DOWNLOAD_SIZE
        } 