import asyncio
import logging
import signal
import sys
from typing import Optional
from pyrogram import Client
from src.config.config import Config
from src.handlers.telegram_bot import TelegramBot
from src.handlers.instagram_monitor import InstagramMonitor
from src.database.database import Database
from src.utils.cache import Cache

# Configure logging
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging to be less verbose
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.telegram_bot: Optional[TelegramBot] = None
        self.instagram_monitor: Optional[InstagramMonitor] = None
        self.db: Optional[Database] = None
        self.cache: Optional[Cache] = None
        self.stop_event = asyncio.Event()

    async def setup(self):
        """Setup application components"""
        try:
            # Initialize database
            self.db = Database()
            
            # Initialize cache
            self.cache = Cache()
            
            # Initialize Telegram bot
            telegram_config = Config.get_telegram_config()
            self.telegram_bot = TelegramBot(
                api_id=telegram_config["api_id"],
                api_hash=telegram_config["api_hash"],
                bot_token=telegram_config["bot_token"]
            )
            await self.telegram_bot.init_session()
            
            # Initialize Instagram monitor
            instagram_config = Config.get_instagram_config()
            self.instagram_monitor = InstagramMonitor(
                username=instagram_config["username"],
                password=instagram_config["password"],
                telegram_bot=self.telegram_bot,
                db=self.db,
                cache=self.cache
            )
            
            logger.debug("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing application: {e}")
            return False

    async def cleanup(self):
        """Cleanup application resources"""
        try:
            if self.telegram_bot:
                await self.telegram_bot.cleanup()
                await self.telegram_bot.bot.stop()
            
            logger.debug("Application resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def signal_handler(self):
        """Handle shutdown signals"""
        logger.debug("Received stop signal...")
        self.stop_event.set()

    async def run(self):
        """Run the application"""
        try:
            if not await self.setup():
                return

            # Start Telegram bot
            logger.debug("Starting Telegram bot...")
            await self.telegram_bot.bot.start()
            logger.debug("Telegram bot started successfully!")
            
            # Start Instagram monitor
            monitor_task = asyncio.create_task(
                self.instagram_monitor.monitor_direct_messages()
            )
            
            # Add signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop = asyncio.get_event_loop()
                loop.add_signal_handler(sig, self.signal_handler)
            
            try:
                await self.stop_event.wait()
            finally:
                # Cancel monitor task
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
                
        except Exception as e:
            logger.error(f"Main application error: {e}")
            raise
        finally:
            await self.cleanup()

async def main():
    """Main entry point"""
    try:
        logger.debug("Bot is starting...")
        app = Application()
        await app.run()
    except KeyboardInterrupt:
        logger.debug("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main()) 