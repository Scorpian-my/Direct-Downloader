import random
import string
import logging
import aiohttp
import os
import aiofiles
from typing import Dict, Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from ..database.database import Database
from ..utils.cache import Cache
from ..utils.rate_limiter import RateLimiter
from ..config.config import Config
from .admin_panel import AdminPanel
from datetime import datetime

# Configure logging to be less verbose
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Only show warnings and errors

class TelegramBot:
    def __init__(self, api_id: str, api_hash: str, bot_token: str):
        self.bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
        self.link_codes: Dict[str, int] = {}
        self.user_data: Dict[int, dict] = {}
        self.linked_users: Dict[int, int] = {}
        self.cache = Cache()
        self.rate_limiter = RateLimiter(
            max_requests=Config.TELEGRAM_RATE_LIMIT,
            time_window=Config.TELEGRAM_RATE_WINDOW
        )
        self.session = None
        self.db = Database()
        self.admin_panel = AdminPanel(self.db, self.bot)

        # Register handlers
        self.bot.add_handler(MessageHandler(self.start, filters.command("start")))
        self.bot.add_handler(CallbackQueryHandler(self.user_info_callback, filters.regex("user_info")))
        self.bot.add_handler(CallbackQueryHandler(self.get_key_callback, filters.regex("get_key")))
        self.bot.add_handler(CallbackQueryHandler(self.handle_admin_callback, filters.regex("^admin_")))

    async def init_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

    def generate_license_code(self) -> str:
        """Generate a unique license code"""
        return "-".join(["".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])

    async def download_video(self, video_url: str) -> Optional[str]:
        """Download video from URL"""
        if not self.session:
            await self.init_session()
            
        try:
            await self.rate_limiter.acquire()
            video_url = str(video_url)
            
            async with self.session.get(video_url) as response:
                if response.status == 200:
                    filename = f"{random.randint(100000, 999999)}.mp4"
                    file_path = os.path.join(Config.DOWNLOAD_DIR, filename)
                    
                    os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            await f.write(chunk)
                    
                    logger.debug(f"Video downloaded successfully: {file_path}")
                    return file_path
                else:
                    logger.error(f"Error downloading video. Status code: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return None

    async def send_video_to_telegram(self, chat_id: int, video_url: str):
        """Send video to Telegram"""
        try:
            file_path = await self.download_video(video_url)
            if file_path:
                try:
                    await self.bot.send_video(
                        chat_id=chat_id,
                        video=file_path,
                        caption="ربات دانلود خودکار تلگرام 🤖"
                    )
                    logger.info(f"✅ ویدیو برای {chat_id} ارسال شد.")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"✅ فایل موقت پاک شد: {file_path}")
            else:
                logger.error("❌ دانلود ویدیو ناموفق بود.")
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ متأسفانه دانلود ویدیو با مشکل مواجه شد. لطفاً دوباره تلاش کنید."
                )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ویدیو به تلگرام: {str(e)}")
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ خطا در ارسال ویدیو. لطفاً دوباره تلاش کنید."
                )
            except Exception as send_error:
                logger.error(f"❌ خطا در ارسال پیام خطا: {str(send_error)}")

    async def start(self, client, message):
        """Handle /start command"""
        chat_id = message.chat.id
        
        if chat_id not in self.user_data:
            connection_code = self.generate_license_code()
            self.user_data[chat_id] = {
                "connection_code": connection_code,
                "name": message.from_user.first_name,
                "username": message.from_user.username
            }
            self.db.add_user(
                telegram_id=chat_id,
                username=message.from_user.username,
                name=message.from_user.first_name,
                connection_code=connection_code
            )
            self.link_codes[connection_code] = chat_id
            
            # Send notification to admin about new user
            admin_message = f"""
👤 New user joined the bot!

📝 Name: {message.from_user.first_name}
🆔 ID: {chat_id}
👤 Username: {message.from_user.username or 'None'}
🔑 Connection Code: {connection_code}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            try:
                await self.bot.send_message(Config.ADMIN_ID, admin_message)
                logger.debug(f"Admin notification sent for new user {chat_id}")
            except Exception as e:
                logger.error(f"Error sending admin notification: {e}")
        
        base_markup = [
            [InlineKeyboardButton("Get Key 🔑", callback_data="get_key")],
            [
                InlineKeyboardButton("Support 📞", url="https://t.me/Dev_Scorpian"),
                InlineKeyboardButton("My Info 📝", callback_data="user_info")
            ]
        ]
        
        if self.admin_panel.is_admin(chat_id):
            base_markup.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")])
        
        markup = InlineKeyboardMarkup(base_markup)

        welcome_text = """
Hello!

Welcome to our bot. With this bot, you can download Instagram videos and posts.

To get started, please use the buttons below:

1. **Support 📞**: Contact support
2. **My Info 📝**: View your account information
3. **Get Key 🗝️**: Get your unique connection code

Please do not share your code with others and send it to our Instagram DM.
Our Instagram ID:
instagram.com/Direct_TDL

After linking, any post or reel you send to our Instagram DM will be automatically downloaded and sent back.
"""
        await message.reply(welcome_text, reply_markup=markup)

    async def user_info_callback(self, client, callback_query):
        """Handle user info callback"""
        chat_id = callback_query.from_user.id
        user_stats = self.db.get_user_stats(chat_id)
        
        if user_stats:
            recent_downloads = self.db.get_recent_downloads(chat_id)
            
            info_keyboard = [
                [InlineKeyboardButton(f"{user_stats['name']}", callback_data="ignore"),
                 InlineKeyboardButton("Your Name", callback_data="ignore")],
                [InlineKeyboardButton(f"{user_stats['username'] or '--'}", callback_data="ignore"),
                 InlineKeyboardButton("Username", callback_data="ignore")],
                [InlineKeyboardButton(f"{user_stats['instagram_id']}", callback_data="ignore"),
                 InlineKeyboardButton("Instagram ID", callback_data="ignore")],
                [InlineKeyboardButton(f"{user_stats['connection_code']}", callback_data="ignore"),
                 InlineKeyboardButton("Connection Code", callback_data="ignore")],
                [InlineKeyboardButton(f"{user_stats['total_downloads']}", callback_data="ignore"),
                 InlineKeyboardButton("Total Downloads", callback_data="ignore")],
                [InlineKeyboardButton(f"{user_stats['created_at']}", callback_data="ignore"),
                 InlineKeyboardButton("Join Date", callback_data="ignore")]
            ]
            
            if recent_downloads:
                info_keyboard.append([InlineKeyboardButton("📥 Recent Downloads:", callback_data="ignore")])
                for download in recent_downloads:
                    caption = download['caption'][:30] + "..." if download['caption'] else "No Caption"
                    info_keyboard.append([
                        InlineKeyboardButton(f"{download['downloaded_at']}", callback_data="ignore"),
                        InlineKeyboardButton(caption, callback_data="ignore")
                    ])
            
            markup = InlineKeyboardMarkup(info_keyboard)
            await client.send_message(chat_id, "📊 Your Information:", reply_markup=markup)
        else:
            await client.send_message(chat_id, "❌ User information not found.")

    async def get_key_callback(self, client, callback_query):
        """Handle get key callback"""
        chat_id = callback_query.from_user.id
        if chat_id in self.user_data:
            code = self.user_data[chat_id]["connection_code"]
            await client.send_message(
                chat_id,
                f"Your unique connection code for two-way communication\nPlease do not share this code with others to maintain your privacy\n`{code}`"
            )
        else:
            await callback_query.answer("❌ User information not found.", show_alert=True)

    async def handle_admin_callback(self, client, callback_query):
        """Handle admin callbacks"""
        chat_id = callback_query.from_user.id
        if not self.admin_panel.is_admin(chat_id):
            await callback_query.answer("❌ You don't have access to this section.", show_alert=True)
            return

        data = callback_query.data
        message_id = callback_query.message.id
        
        if data == "admin_panel":
            await self.admin_panel.show_admin_panel(chat_id, message_id)
        elif data == "admin_stats":
            await self.admin_panel.show_stats(chat_id, message_id)
        elif data == "admin_users":
            await self.admin_panel.show_users_list(chat_id, message_id)
        elif data == "admin_broadcast":
            await self.admin_panel.start_broadcast(chat_id, message_id)
        elif data == "admin_search":
            await self.admin_panel.start_user_search(chat_id, message_id)
        elif data == "admin_settings":
            await self.admin_panel.show_settings(chat_id, message_id)
        elif data == "back_to_main":
            await self.admin_panel.back_to_main_menu(chat_id, message_id)

    async def handle_message(self, client, message):
        """Handle regular messages"""
        chat_id = message.chat.id
        admin_state = self.db.get_admin_state(chat_id)
        
        if admin_state == "waiting_broadcast":
            await self.handle_broadcast_message(message)
        elif admin_state == "waiting_user_search":
            await self.handle_user_search_message(message)
        else:
            # Process normal messages
            pass

    async def handle_broadcast_message(self, message):
        """Handle broadcast message"""
        chat_id = message.chat.id
        if not self.admin_panel.is_admin(chat_id):
            return

        users = self.db.get_all_users()
        success_count = 0
        fail_count = 0
        
        await message.reply("📨 در حال ارسال پیام همگانی...")
        
        for user in users:
            try:
                await self.bot.send_message(user["telegram_id"], message.text)
                success_count += 1
            except Exception as e:
                logger.error(f"❌ خطا در ارسال پیام به کاربر {user['telegram_id']}: {e}")
                fail_count += 1
        
        await message.reply(f"""
✅ ارسال پیام همگانی به پایان رسید:

✅ موفق: {success_count}
❌ ناموفق: {fail_count}
""")
        
        self.db.set_admin_state(chat_id, None)

    async def handle_user_search_message(self, message):
        """Handle user search message"""
        chat_id = message.chat.id
        if not self.admin_panel.is_admin(chat_id):
            return

        search_query = message.text
        users = self.db.search_users(search_query)
        
        if users:
            text = "🔍 نتایج جستجو:\n\n"
            for user in users:
                text += f"""
👤 نام: {user['name']}
🆔 شناسه: {user['telegram_id']}
📱 اینستاگرام: {user['instagram_id']}
📥 تعداد دانلودها: {user['total_downloads']}
-------------------
"""
        else:
            text = "❌ کاربری یافت نشد."
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
        ])
        
        await message.reply(text, reply_markup=markup)
        self.db.set_admin_state(chat_id, None) 