import os
import sys
import re
from typing import Dict, Any

def validate_api_id(api_id: str) -> bool:
    """Validate Telegram API ID"""
    return api_id.isdigit() and len(api_id) >= 5

def validate_api_hash(api_hash: str) -> bool:
    """Validate Telegram API Hash"""
    return bool(re.match(r'^[a-f0-9]{32}$', api_hash))

def validate_bot_token(bot_token: str) -> bool:
    """Validate Telegram Bot Token"""
    return bool(re.match(r'^\d+:[A-Za-z0-9_-]{35}$', bot_token))

def validate_telegram_id(telegram_id: str) -> bool:
    """Validate Telegram User ID"""
    return telegram_id.isdigit()

def get_input(prompt: str, validator=None) -> str:
    """Get user input with validation"""
    while True:
        value = input(prompt).strip()
        if validator and not validator(value):
            print("❌ Invalid input. Please try again.")
            continue
        return value

def create_env_file(config: Dict[str, Any]):
    """Create .env file with configuration"""
    env_content = f"""# Telegram Configuration
TELEGRAM_API_ID={config['api_id']}
TELEGRAM_API_HASH={config['api_hash']}
TELEGRAM_BOT_TOKEN={config['bot_token']}
ADMIN_ID={config['admin_id']}

# Instagram Configuration
INSTAGRAM_USERNAME={config['instagram_username']}
INSTAGRAM_PASSWORD={config['instagram_password']}

# Optional Instagram Proxy (leave empty if not using)
INSTAGRAM_PROXY=

# Database Configuration
DATABASE_PATH=bot_database.db

# Rate Limiting Configuration
TELEGRAM_RATE_LIMIT=30
TELEGRAM_RATE_WINDOW=60
INSTAGRAM_RATE_LIMIT=20
INSTAGRAM_RATE_WINDOW=60

# Cache Configuration
MESSAGE_CACHE_TTL=3600
USER_CACHE_TTL=7200
MESSAGE_CACHE_SIZE=1000
USER_CACHE_SIZE=500

# Download Configuration
DOWNLOAD_DIR=downloads
MAX_DOWNLOAD_SIZE=52428800
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

def check_existing_config() -> bool:
    """Check if configuration already exists"""
    return os.path.exists('.env')

def main():
    """Main setup function"""
    print("🔧 Instagram Direct Downloader Bot Setup")
    print("=======================================")
    
    if check_existing_config():
        print("\n⚠️ Configuration file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Please enter the following information:")
    print("----------------------------------------")
    
    config = {
        'api_id': get_input("Enter Telegram API ID: ", validate_api_id),
        'api_hash': get_input("Enter Telegram API Hash: ", validate_api_hash),
        'bot_token': get_input("Enter Telegram Bot Token: ", validate_bot_token),
        'admin_id': get_input("Enter Admin Telegram ID: ", validate_telegram_id),
        'instagram_username': get_input("Enter Instagram Username: "),
        'instagram_password': get_input("Enter Instagram Password: ")
    }
    
    print("\n📋 Configuration Summary:")
    print("------------------------")
    print(f"Telegram API ID: {config['api_id']}")
    print(f"Telegram API Hash: {config['api_hash']}")
    print(f"Telegram Bot Token: {config['bot_token']}")
    print(f"Admin ID: {config['admin_id']}")
    print(f"Instagram Username: {config['instagram_username']}")
    print(f"Instagram Password: {'*' * len(config['instagram_password'])}")
    
    response = input("\nIs this information correct? (y/N): ").strip().lower()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    try:
        create_env_file(config)
        print("\n✅ Configuration saved successfully!")
        print("You can now run the bot using: python main.py")
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 