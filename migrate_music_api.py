#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加MusicAPIConfig表
"""

import sqlite3
import os

def migrate_database():
    db_path = 'instance/db.sqlite3'
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，无需迁移")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查music_api_config表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='music_api_config'")
        if cursor.fetchone() is None:
            print("创建music_api_config表...")
            cursor.execute("""
                CREATE TABLE music_api_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    api_url VARCHAR(200) NOT NULL,
                    api_key VARCHAR(200),
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入默认的AceStep配置
            cursor.execute("""
                INSERT INTO music_api_config (provider, name, api_url, is_active)
                VALUES ('acestep', 'AceStep本地服务', 'http://127.0.0.1:7865/', 1)
            """)
            
            conn.commit()
            print("迁移完成！已创建music_api_config表并添加默认AceStep配置")
        else:
            print("music_api_config表已存在，无需迁移")
            
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database() 