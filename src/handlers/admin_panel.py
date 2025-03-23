from typing import Dict, List
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..database.database import Database
from ..config.config import Config

class AdminPanel:
    def __init__(self, db: Database, bot: Client):
        self.db = db
        self.bot = bot
        self.admin_id = Config.ADMIN_ID

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.admin_id

    async def show_admin_panel(self, chat_id: int, message_id: int = None):
        """Show admin panel"""
        if not self.is_admin(chat_id):
            return

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 General Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Users List", callback_data="admin_users")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
        ])
        
        text = "🔧 Admin Panel\nPlease select an option:"
        
        if message_id:
            message = await self.bot.get_messages(chat_id, message_id)
            await message.edit_text(text, reply_markup=markup)
        else:
            await self.bot.send_message(chat_id, text, reply_markup=markup)

    async def show_stats(self, chat_id: int, message_id: int):
        """Show admin statistics"""
        stats = self.db.get_admin_stats()
        text = f"""
📊 System Statistics:

👥 Total Users: {stats['total_users']}
📥 Total Downloads: {stats['total_downloads']}
📅 Users Today: {stats['users_today']}
📥 Downloads Today: {stats['downloads_today']}
"""
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]
        ])
        message = await self.bot.get_messages(chat_id, message_id)
        await message.edit_text(text, reply_markup=markup)

    async def show_users_list(self, chat_id: int, message_id: int):
        """Show users list"""
        users = self.db.get_all_users()
        text = "👥 Users List:\n\n"
        
        for user in users:
            text += f"""
👤 Name: {user['name']}
🆔 ID: {user['telegram_id']}
📱 Instagram: {user['instagram_id']}
📥 Downloads: {user['total_downloads']}
📅 Join Date: {user['created_at']}
-------------------
"""
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]
        ])
        message = await self.bot.get_messages(chat_id, message_id)
        await message.edit_text(text, reply_markup=markup)

    async def back_to_main_menu(self, chat_id: int, message_id: int):
        """Return to main menu"""
        base_markup = [
            [InlineKeyboardButton("Get Key 🔑", callback_data="get_key")],
            [
                InlineKeyboardButton("Support 📞", url="https://t.me/Dev_Scorpian"),
                InlineKeyboardButton("My Info 📝", callback_data="user_info")
            ],
            [InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")]
        ]
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
        message = await self.bot.get_messages(chat_id, message_id)
        await message.edit_text(welcome_text, reply_markup=markup) 