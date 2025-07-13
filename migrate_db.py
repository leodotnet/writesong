#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加system_prompt字段到LLMConfig表
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
        # 检查system_prompt字段是否已存在
        cursor.execute("PRAGMA table_info(llm_config)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'system_prompt' not in columns:
            print("添加system_prompt字段到llm_config表...")
            cursor.execute("""
                ALTER TABLE llm_config 
                ADD COLUMN system_prompt TEXT 
                DEFAULT 'Generate suno-style lyric based on the following description:'
            """)
            
            # 更新现有记录的系统提示词
            cursor.execute("""
                UPDATE llm_config 
                SET system_prompt = 'Generate suno-style lyric based on the following description: {prompt}'
                WHERE system_prompt IS NULL OR system_prompt = 'Generate suno-style lyric based on the following description:'
            """)
            
            conn.commit()
            print("迁移完成！")
        else:
            print("system_prompt字段已存在，无需迁移")
            
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database() 