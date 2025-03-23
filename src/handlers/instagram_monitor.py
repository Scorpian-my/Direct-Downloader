import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from instagrapi import Client as InstaClient
from ..database.database import Database
from ..utils.cache import Cache
from ..utils.rate_limiter import RateLimiter
from ..config.config import Config

# Configure logging to be less verbose
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Only show warnings and errors

class InstagramMonitor:
    def __init__(self, username: str, password: str, telegram_bot, db: Database, cache: Cache):
        self.client = InstaClient()
        self.telegram_bot = telegram_bot
        self.db = db
        self.cache = cache
        self.username = username
        self.password = password
        self.last_seen_message = None
        self.rate_limiter = RateLimiter(
            max_requests=Config.INSTAGRAM_RATE_LIMIT,
            time_window=Config.INSTAGRAM_RATE_WINDOW
        )
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300
        self.loop = asyncio.get_event_loop()
        self.is_running = False
        
        # Set up proxy if configured
        if hasattr(Config, 'INSTAGRAM_PROXY'):
            self.client.set_proxy(Config.INSTAGRAM_PROXY)

    async def run_sync(self, func, *args, **kwargs):
        """Run sync functions in thread pool"""
        return await self.loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def login(self) -> bool:
        """Login to Instagram"""
        try:
            await self.rate_limiter.acquire()
            self.client.login(self.username, self.password)
            logger.debug("Successfully logged in to Instagram")
            return True
        except Exception as e:
            error_msg = str(e)
            if "IP address" in error_msg and "blacklist" in error_msg:
                logger.error("IP address is blacklisted by Instagram. Please use a VPN or wait.")
                # Increase reconnect delay significantly for IP blacklist
                self.reconnect_delay = min(self.reconnect_delay * 4, self.max_reconnect_delay)
            else:
                logger.error(f"Login error: {error_msg}")
            return False

    async def process_message(self, thread, msg):
        """Process Instagram message"""
        try:
            await self.rate_limiter.acquire()
            
            # Check for duplicate messages
            message_id = f"{thread.id}_{msg.id}"
            if self.cache.get_message(message_id):
                return
                
            # Skip messages from the bot itself
            if msg.user_id == self.client.user_id:
                logger.debug("Skipping message from bot")
                return
            
            # Skip if message is empty
            if not msg.text and not msg.clip:
                return
                
            self.cache.set_message(message_id, {
                "processed_at": datetime.now().isoformat(),
                "type": "text" if msg.text else "media"
            })

            if msg.text:
                await self.handle_text_message(thread, msg)
            elif msg.clip:
                await self.handle_media_message(thread, msg)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_text_message(self, thread, msg):
        """Handle text messages"""
        try:
            # Skip if message is from bot
            if msg.user_id == self.client.user_id:
                logger.debug("Skipping message from bot")
                return
                
            code = msg.text.strip()
            logger.debug(f"Received text message: {code}")
            
            # Handle ping-pong test
            if code.lower() == "ping":
                logger.debug("Received ping request")
                await self.run_sync(self.client.direct_answer, thread.id, "Im Online 🌟")
                return
            if code.lower() == "hello":
                await self.run_sync(self.client.direct_answer, thread.id, "Hello! Welcome to Direct Downloader Bot 🌟\nTo download videos and photos, please send your connection code that you received from Telegram")
                return
                
            # Check if user is already linked
            if msg.user_id in self.telegram_bot.linked_users:
                logger.debug(f"User {msg.user_id} is already linked")
                return
                
            logger.debug(f"Available codes in bot: {self.telegram_bot.link_codes}")
            
            # Clean up the code (remove any extra spaces or special characters)
            code = code.replace(" ", "").replace("-", "").upper()
            
            # Check if the code exists in link_codes
            found_code = None
            for stored_code in self.telegram_bot.link_codes.keys():
                stored_code_clean = stored_code.replace(" ", "").replace("-", "").upper()
                logger.debug(f"Comparing codes: {code} with {stored_code_clean}")
                if stored_code_clean == code:
                    found_code = stored_code
                    break
            
            if found_code:
                logger.debug(f"Valid code found: {found_code}")
                await self.link_user(thread, msg, found_code)
            else:
                logger.debug(f"Invalid code: {code}")
                logger.debug(f"Available codes: {list(self.telegram_bot.link_codes.keys())}")
                logger.debug(f"Available codes (cleaned): {[c.replace(' ', '').replace('-', '').upper() for c in self.telegram_bot.link_codes.keys()]}")
                
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            logger.exception(e)

    async def handle_media_message(self, thread, msg):
        """Handle media messages"""
        try:
            link = None
            caption = None
            
            logger.info(f"پردازش پیام مدیا: {msg}")
            logger.info(f"نوع clip: {type(msg.clip)}")
            
            if hasattr(msg.clip, "video_url"):
                link = str(msg.clip.video_url)
                logger.info(f"video_url یافت شد: {link}")
            elif hasattr(msg.clip, "progressive_download_url"):
                link = str(msg.clip.progressive_download_url)
                logger.info(f"progressive_download_url یافت شد: {link}")
            elif hasattr(msg.clip, "url"):
                link = str(msg.clip.url)
                logger.info(f"url یافت شد: {link}")
            
            if hasattr(msg.clip, "caption_text"):
                caption = str(msg.clip.caption_text)
            
            if link:
                logger.info(f"تلاش برای دانلود ویدیو از لینک: {link}")
                await self.send_media_to_telegram(thread, msg, link, caption)
            else:
                logger.error("❌ هیچ لینک ویدیویی یافت نشد")
                await self.run_sync(self.client.direct_answer, thread.id, "❌ متأسفانه نمی‌توانم این نوع محتوا را دانلود کنم.")
        except Exception as e:
            logger.error(f"❌ خطا در پردازش پیام مدیا: {str(e)}")
            await self.run_sync(self.client.direct_answer, thread.id, "❌ خطا در پردازش ویدیو")

    async def link_user(self, thread, msg, code):
        """Link Instagram user with Telegram user"""
        try:
            logger.info(f"🔄 شروع فرآیند لینک کردن با کد: {code}")
            logger.info(f"👤 شناسه کاربر اینستاگرام: {msg.user_id}")
            logger.info(f"🔑 کدهای موجود قبل از لینک: {self.telegram_bot.link_codes}")
            
            # Clean up the code for comparison
            code_clean = code.replace(" ", "").replace("-", "").upper()
            
            # Find the original code in link_codes
            original_code = None
            for stored_code in self.telegram_bot.link_codes.keys():
                if stored_code.replace(" ", "").replace("-", "").upper() == code_clean:
                    original_code = stored_code
                    break
            
            if not original_code:
                logger.error(f"❌ کد {code} در لیست کدهای فعال وجود ندارد")
                await self.run_sync(self.client.direct_answer, thread.id, "❌ کد نامعتبر یا منقضی شده است.")
                return
                
            tg_chat_id = self.telegram_bot.link_codes[original_code]
            logger.info(f"🔗 شناسه چت تلگرام: {tg_chat_id}")
            
            # Store the link before removing the code
            self.telegram_bot.linked_users[msg.user_id] = tg_chat_id
            
            try:
                info = await self.run_sync(self.client.user_info, msg.user_id)
                logger.info(f"📱 اطلاعات کاربر اینستاگرام: {info.username}")
                
                if tg_chat_id not in self.telegram_bot.user_data:
                    self.telegram_bot.user_data[tg_chat_id] = {}
                    
                self.telegram_bot.user_data[tg_chat_id]["instagram_id"] = info.username
                self.cache.set_user(
                    str(tg_chat_id),
                    self.telegram_bot.user_data[tg_chat_id]
                )
                
                # Update Instagram ID in database
                self.db.update_instagram_id(tg_chat_id, info.username)
                
                # Only remove the code after successful linking
                del self.telegram_bot.link_codes[original_code]
                logger.info(f"🔑 کدهای موجود بعد از لینک: {self.telegram_bot.link_codes}")
                
                # Send confirmation messages
                await self.run_sync(self.client.direct_answer, thread.id, "✅ حساب شما با تلگرام برقرار شد!")
                logger.info(f"✅ لینک شد: Instagram {msg.user_id} به Telegram {tg_chat_id}")
                
                try:
                    await self.telegram_bot.bot.send_message(tg_chat_id, "✅ اتصال برقرار است")
                    logger.info(f"✅ پیام تأیید به تلگرام ارسال شد")
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال پیام به تلگرام: {e}")
                    
            except Exception as e:
                logger.error(f"❌ خطا در دریافت اطلاعات اینستاگرام: {e}")
                # Don't remove the code if there was an error
                await self.run_sync(self.client.direct_answer, thread.id, "❌ خطا در دریافت اطلاعات اینستاگرام. لطفاً دوباره تلاش کنید.")
                
        except Exception as e:
            logger.error(f"❌ خطا در فرآیند لینک کردن: {e}")
            logger.exception(e)
            await self.run_sync(self.client.direct_answer, thread.id, "❌ خطا در برقراری اتصال. لطفاً دوباره تلاش کنید.")

    async def send_media_to_telegram(self, thread, msg, link, caption):
        """Send media to Telegram"""
        try:
            tg_chat_id = self.telegram_bot.linked_users.get(msg.user_id)
            if not tg_chat_id:
                await self.run_sync(self.client.direct_answer, thread.id, "❌ شما به ربات تلگرام متصل نیستید.")
                return

            await self.run_sync(self.client.direct_answer, thread.id, "در حال ارسال فیلم به تلگرام 🔄")
            
            if not isinstance(link, str):
                logger.error(f"❌ نوع لینک نامعتبر است: {type(link)}")
                link = str(link)
            
            logger.info(f"تلاش برای دانلود و ارسال ویدیو به تلگرام. لینک: {link}")
            await self.telegram_bot.send_video_to_telegram(tg_chat_id, link)
            
            # Record download in database
            self.db.add_download(
                telegram_id=tg_chat_id,
                instagram_id=msg.user_id,
                media_url=link,
                caption=caption
            )
            
            if caption:
                await self.telegram_bot.bot.send_message(tg_chat_id, text=caption)
            
            await self.run_sync(self.client.direct_answer, thread.id, "با موفقیت ارسال شد ✅")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ویدیو به تلگرام: {str(e)}")
            await self.run_sync(self.client.direct_answer, thread.id, "❌ خطا در ارسال ویدیو")

    async def monitor_direct_messages(self):
        """Monitor Instagram direct messages"""
        processed_messages = set()  # Set to store processed message IDs
        while True:
            try:
                if not await self.login():
                    await asyncio.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                    continue

                self.reconnect_delay = 1
                threads = await self.run_sync(self.client.direct_threads)
                
                for thread in threads:
                    try:
                        messages = await self.run_sync(self.client.direct_messages, thread.id, 5)
                        if not messages:
                            continue
                            
                        for msg in messages:
                            # Create unique message ID
                            message_id = f"{thread.id}_{msg.id}"
                            
                            # Skip if already processed
                            if message_id in processed_messages:
                                continue
                                
                            # Add to processed set
                            processed_messages.add(message_id)
                            
                            # Process the message
                            await self.process_message(thread, msg)
                            
                            # Keep set size manageable
                            if len(processed_messages) > 1000:
                                processed_messages.clear()
                                
                    except Exception as e:
                        logger.error(f"❌ خطا در پردازش thread {thread.id}: {e}")
                        continue

                await asyncio.sleep(5)  # Increased delay to reduce API calls
            except Exception as e:
                logger.error(f"❌ خطا در بررسی دایرکت‌های اینستاگرام: {e}")
                await asyncio.sleep(self.reconnect_delay) 