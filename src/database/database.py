import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    instagram_id TEXT,
                    connection_code TEXT,
                    created_at TIMESTAMP,
                    total_downloads INTEGER DEFAULT 0
                )
            ''')
            
            # Downloads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    instagram_id INTEGER,
                    media_url TEXT,
                    caption TEXT,
                    downloaded_at TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    daily_download_limit INTEGER DEFAULT 50,
                    download_cooldown INTEGER DEFAULT 60
                )
            ''')
            
            # Admin states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_states (
                    admin_id INTEGER PRIMARY KEY,
                    state TEXT
                )
            ''')
            
            # Add default settings
            cursor.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
            
            conn.commit()

    def add_user(self, telegram_id: int, username: str, name: str, connection_code: str):
        """Add a new user to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (telegram_id, username, name, connection_code, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, username, name, connection_code, datetime.now()))
            conn.commit()

    def update_instagram_id(self, telegram_id: int, instagram_id: str):
        """Update user's Instagram ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET instagram_id = ? WHERE telegram_id = ?
            ''', (instagram_id, telegram_id))
            conn.commit()

    def add_download(self, telegram_id: int, instagram_id: int, media_url: str, caption: str = None):
        """Add a new download record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads (telegram_id, instagram_id, media_url, caption, downloaded_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, instagram_id, media_url, caption, datetime.now()))
            
            cursor.execute('''
                UPDATE users SET total_downloads = total_downloads + 1
                WHERE telegram_id = ?
            ''', (telegram_id,))
            
            conn.commit()

    def get_user_stats(self, telegram_id: int) -> Optional[Dict]:
        """Get user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.*, COUNT(d.id) as total_downloads
                FROM users u
                LEFT JOIN downloads d ON u.telegram_id = d.telegram_id
                WHERE u.telegram_id = ?
                GROUP BY u.telegram_id
            ''', (telegram_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "telegram_id": row[0],
                    "username": row[1],
                    "name": row[2],
                    "instagram_id": row[3],
                    "connection_code": row[4],
                    "created_at": row[5],
                    "total_downloads": row[6]
                }
            return None

    def get_recent_downloads(self, telegram_id: int, limit: int = 5) -> List[Dict]:
        """Get recent downloads for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT media_url, caption, downloaded_at
                FROM downloads
                WHERE telegram_id = ?
                ORDER BY downloaded_at DESC
                LIMIT ?
            ''', (telegram_id, limit))
            
            return [{
                "media_url": row[0],
                "caption": row[1],
                "downloaded_at": row[2]
            } for row in cursor.fetchall()]

    def get_admin_stats(self) -> Dict:
        """Get admin statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM downloads")
            total_downloads = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = DATE('now')
            """)
            users_today = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM downloads 
                WHERE DATE(downloaded_at) = DATE('now')
            """)
            downloads_today = cursor.fetchone()[0]
            
            return {
                "total_users": total_users,
                "total_downloads": total_downloads,
                "users_today": users_today,
                "downloads_today": downloads_today
            }

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telegram_id, username, name, instagram_id, 
                       total_downloads, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            
            return [{
                "telegram_id": row[0],
                "username": row[1],
                "name": row[2],
                "instagram_id": row[3],
                "total_downloads": row[4],
                "created_at": row[5]
            } for row in cursor.fetchall()]

    def get_settings(self) -> Dict:
        """Get system settings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            row = cursor.fetchone()
            if row:
                return {
                    "daily_download_limit": row[1],
                    "download_cooldown": row[2]
                }
            return {"daily_download_limit": 50, "download_cooldown": 60}

    def set_admin_state(self, admin_id: int, state: str):
        """Set admin state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO admin_states (admin_id, state)
                VALUES (?, ?)
            """, (admin_id, state))
            conn.commit()

    def get_admin_state(self, admin_id: int) -> Optional[str]:
        """Get admin state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state FROM admin_states WHERE admin_id = ?", (admin_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def search_users(self, query: str) -> List[Dict]:
        """Search users by query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telegram_id, username, name, instagram_id, 
                       total_downloads, created_at
                FROM users
                WHERE username LIKE ? OR name LIKE ? OR instagram_id LIKE ?
                ORDER BY created_at DESC
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            
            return [{
                "telegram_id": row[0],
                "username": row[1],
                "name": row[2],
                "instagram_id": row[3],
                "total_downloads": row[4],
                "created_at": row[5]
            } for row in cursor.fetchall()] 