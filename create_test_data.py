#!/usr/bin/env python3
"""
手动创建测试数据
"""

import requests
import sqlite3
import os

def create_test_data():
    """创建测试数据"""
    base_url = "http://localhost:8527"
    session = requests.Session()
    
    print("创建测试数据...")
    
    # 1. 注册用户
    print("1. 注册用户...")
    register_data = {
        'username': 'testuser_data',
        'password': 'testpass123'
    }
    response = session.post(f"{base_url}/signup", data=register_data)
    print(f"注册状态码: {response.status_code}")
    
    # 2. 登录
    print("2. 登录...")
    login_data = {
        'username': 'testuser_data',
        'password': 'testpass123'
    }
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"登录状态码: {response.status_code}")
    
    # 3. 生成歌词
    print("3. 生成歌词...")
    lyric_data = {
        'prompt': '写一首关于春天的歌'
    }
    response = session.post(f"{base_url}/generate_lyric", data=lyric_data)
    print(f"生成歌词状态码: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                lyrics_text = result.get('lyric', '测试歌词内容')
                print("✅ 歌词生成成功")
            else:
                print("❌ 歌词生成失败")
                lyrics_text = "测试歌词内容\n用于测试参考音频功能"
        except:
            print("❌ 歌词生成响应解析失败")
            lyrics_text = "测试歌词内容\n用于测试参考音频功能"
    else:
        print("❌ 歌词生成请求失败")
        lyrics_text = "测试歌词内容\n用于测试参考音频功能"
    
    # 4. 保存歌词
    print("4. 保存歌词...")
    save_data = {
        'lyric_name': '测试歌词_数据',
        'lyric': lyrics_text
    }
    response = session.post(f"{base_url}/save_song", data=save_data)
    print(f"保存歌词状态码: {response.status_code}")
    
    # 5. 检查数据库
    print("5. 检查数据库...")
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库表: {tables}")
        
        if tables:
            # 检查用户表
            cursor.execute("SELECT * FROM user LIMIT 5;")
            users = cursor.fetchall()
            print(f"用户记录: {users}")
            
            # 检查歌词表
            cursor.execute("SELECT * FROM lyrics LIMIT 5;")
            lyrics = cursor.fetchall()
            print(f"歌词记录: {lyrics}")
        
        conn.close()
    except Exception as e:
        print(f"数据库查询错误: {e}")

if __name__ == "__main__":
    create_test_data() 