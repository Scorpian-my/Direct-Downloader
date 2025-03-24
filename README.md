<div align="center">

# Instagram Direct Downloader Bot

<img src="https://github.com/Scorpian-my/File-Manager/blob/main/Direct.png" alt="Direct Downloader Logo" width="200"/>

<br/>

![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)

[![Stars](https://img.shields.io/github/stars/Scorpian-my/Direct-Downloader?style=social)](https://github.com/Scorpian-my/Direct-Downloader/stargazers)
[![Forks](https://img.shields.io/github/forks/Scorpian-my/Direct-Downloader?style=social)](https://github.com/Scorpian-my/Direct-Downloader/network)
[![Issues](https://img.shields.io/github/issues/Scorpian-my/Direct-Downloader?style=social)](https://github.com/Scorpian-my/Direct-Downloader/issues)

</div>

## 📝 Description

A powerful Telegram bot that enables users to download media content from Instagram Direct messages. This bot provides a seamless experience for downloading photos, videos, and other media types directly to your Telegram chat.

## ✨ Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🔐 Authentication | Secure Instagram login with session management |
| 📥 Downloads | Support for various media types (photos, videos, voice messages) |
| 📊 Admin Panel | User statistics and management interface |
| ⚡ Performance | Rate limiting and efficient caching system |
| 🔒 Security | Input validation and secure credential storage |

</div>

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- Telegram API ID and API Hash
- Instagram account credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Scorpian-my/Direct-Downloader.git
cd Direct-Downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup script:
```bash
python setup.py
```

4. Follow the prompts to configure:
   - Telegram API credentials
   - Instagram account details
   - Admin settings

## ⚙️ Configuration

The bot uses environment variables for configuration. Create a `.env` file with:

```env
# Telegram Settings
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_ID=your_admin_id

# Instagram Settings
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_PROXY=  # Optional

# System Settings
DATABASE_PATH=bot_database.db
DOWNLOAD_DIR=downloads
MAX_DOWNLOAD_SIZE=52428800
```

## 🎮 Usage

1. Start the bot:
```bash
python main.py
```

2. In Telegram:
   - Start chat with your bot
   - Send `/start` to begin
   - Send Instagram direct message links to download content

3. Admin Panel (`/start`):
   - View general statistics
   - Manage user list
   - Search users
   - Return to main menu

## 📁 Project Structure

```
Direct-Downloader/
├── main.py                 # Main entry point
├── setup.py               # Configuration setup
├── requirements.txt       # Dependencies
├── src/
│   ├── config/           # Configuration files
│   ├── database/         # Database operations
│   ├── handlers/         # Message handlers
│   ├── models/           # Data models
│   ├── sessions/         # Session files
│   └── utils/            # Utilities
└── downloads/            # Media storage
```

## 🔒 Security

- Rate limiting to prevent abuse
- Secure session management
- Input validation
- Protected credential storage
- Comprehensive error handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

For support or questions, contact the developer:
- Telegram: [@Dev_Scorpian](https://t.me/Dev_Scorpian)

## 💎 Crypto Support

If you find this project helpful, you can support the developer with cryptocurrency:

<div align="center">

| Network | Address |
|---------|---------|
| TRX (TRON) | `THBRkdaEmujtZXBvN6Wok9DX5exGNVNrdP` |
| TON (TON) | `UQCsCqmornHmMH7OgQACRPAEyEBxbT7bC_WQIk5-PGgr4vBM` |
| BTC (Bitcoin) | `bc1qykg34s3pfwr4knzdj28hkkvwjqtzscqmsvsyr9` |

</div>

## 📜 Copyright

© 2025 [@Dev_Scorpian](https://t.me/Dev_Scorpian). All rights reserved.

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) for Telegram API
- [Instagrapi](https://github.com/adw0rd/instagrapi) for Instagram API
- All contributors and users

---

<div align="center">
Made with ❤️
</div> 
