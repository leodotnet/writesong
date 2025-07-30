#!/usr/bin/env python3
"""
测试修复后的参考音频功能
"""

import requests
import os

def test_ref_audio_fix():
    """测试修复后的参考音频功能"""
    base_url = "http://localhost:8527"
    session = requests.Session()
    
    # 使用现有的测试音频文件
    test_audio_path = "song/356596524.mp3"
    
    if not os.path.exists(test_audio_path):
        print(f"❌ 测试音频文件不存在: {test_audio_path}")
        return
    
    print("开始测试修复后的参考音频功能...")
    
    try:
        # 1. 注册并登录
        print("1. 注册并登录...")
        register_data = {
            'username': 'testuser_direct',
            'password': 'testpass123'
        }
        session.post(f"{base_url}/signup", data=register_data)
        session.post(f"{base_url}/login", data=register_data)
        
        # 2. 测试参考音频上传
        print("2. 测试参考音频上传...")
        
        with open(test_audio_path, 'rb') as f:
            files = {
                'ref_audio': ('356596524.mp3', f, 'audio/mpeg')
            }
            data = {
                'lyrics': '测试歌词内容\n用于测试修复后的参考音频功能',
                'format': 'mp3',
                'prompt': 'test, pop, melodic, 120 BPM'
            }
            
            print("发送参考音频上传请求...")
            response = session.post(f"{base_url}/generate_song_with_acestep/12", files=files, data=data)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print("✅ 参考音频功能修复成功！")
                        print(f"生成的歌曲URL: {result.get('song_url')}")
                        
                        # 检查uploads目录是否创建了文件
                        uploads_dir = "uploads"
                        if os.path.exists(uploads_dir):
                            files_in_uploads = os.listdir(uploads_dir)
                            ref_audio_files = [f for f in files_in_uploads if f.startswith('ref_audio_')]
                            print(f"✅ uploads目录已创建，包含 {len(ref_audio_files)} 个参考音频文件")
                            for file in ref_audio_files:
                                print(f"  - {file}")
                        else:
                            print("❌ uploads目录不存在")
                            
                    else:
                        print("❌ 参考音频功能测试失败")
                        print(f"错误信息: {result.get('error')}")
                except Exception as e:
                    print("❌ 响应解析失败")
                    print(f"错误: {e}")
                    print("响应内容:", response.text[:200])
            else:
                print("❌ 参考音频上传请求失败")
                print("响应内容:", response.text[:200])
                
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    finally:
        print("测试完成")

if __name__ == "__main__":
    test_ref_audio_fix() 