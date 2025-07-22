#!/usr/bin/env python3
"""
WriteSong 离线功能测试脚本
"""

import requests
import time
import os

def test_server_connection():
    """测试服务器连接"""
    print("🔍 测试服务器连接...")
    try:
        response = requests.get("http://127.0.0.1:8527/", timeout=5)
        if response.status_code == 200 or response.status_code == 302:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_static_files():
    """测试静态文件访问"""
    print("\n📁 测试静态文件访问...")
    
    static_files = [
        "/static/css/offline.css",
        "/static/js/offline.js",
        "/static/css/bootstrap.min.css",
        "/static/js/jquery.min.js",
        "/static/js/bootstrap.min.js",
        "/static/js/popper.min.js"
    ]
    
    all_ok = True
    for file_path in static_files:
        try:
            response = requests.get(f"http://127.0.0.1:8527{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path} - 正常")
            else:
                print(f"❌ {file_path} - 状态码: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {file_path} - 错误: {e}")
            all_ok = False
    
    return all_ok

def test_network_status_page():
    """测试网络状态检测页面"""
    print("\n🌐 测试网络状态检测页面...")
    try:
        response = requests.get("http://127.0.0.1:8527/network-status", timeout=5)
        if response.status_code == 200:
            if "网络状态检测" in response.text:
                print("✅ 网络状态检测页面正常")
                return True
            else:
                print("❌ 网络状态检测页面内容异常")
                return False
        else:
            print(f"❌ 网络状态检测页面响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 网络状态检测页面访问失败: {e}")
        return False

def check_file_sizes():
    """检查静态文件大小"""
    print("\n📊 检查静态文件大小...")
    
    static_dir = "static"
    if not os.path.exists(static_dir):
        print("❌ static目录不存在")
        return False
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1
            print(f"📄 {file_path} - {size:,} bytes")
    
    print(f"\n📈 总计: {file_count} 个文件, {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    return True

def main():
    """主测试函数"""
    print("🚀 WriteSong 离线功能测试")
    print("=" * 50)
    
    # 测试服务器连接
    if not test_server_connection():
        print("\n❌ 服务器未运行，请先启动应用")
        return
    
    # 测试静态文件
    if not test_static_files():
        print("\n❌ 静态文件测试失败")
        return
    
    # 测试网络状态页面
    if not test_network_status_page():
        print("\n❌ 网络状态检测页面测试失败")
        return
    
    # 检查文件大小
    check_file_sizes()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！")
    print("\n📋 使用说明:")
    print("1. 访问 http://127.0.0.1:8527/ 查看应用")
    print("2. 访问 http://127.0.0.1:8527/network-status 查看网络状态")
    print("3. 断开网络连接测试离线功能")
    print("4. 重新连接网络测试自动恢复功能")

if __name__ == "__main__":
    main() 