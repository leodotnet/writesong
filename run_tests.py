#!/usr/bin/env python3
"""
一键运行所有测试脚本
"""

import subprocess
import sys
import os
import time

def run_test(test_name, test_file, description):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_name}")
    print(f"描述: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 测试通过")
            print("输出:")
            print(result.stdout)
        else:
            print("❌ 测试失败")
            print("错误输出:")
            print(result.stderr)
            print("标准输出:")
            print(result.stdout)
            
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
    except FileNotFoundError:
        print(f"❌ 测试文件不存在: {test_file}")
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")

def check_app_running():
    """检查应用是否正在运行"""
    try:
        import requests
        response = requests.get("http://localhost:8527", timeout=5)
        return response.status_code == 200 or response.status_code == 302
    except:
        return False

def main():
    """主函数"""
    print("🚀 开始运行所有测试")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查应用是否运行
    print("\n检查应用状态...")
    if check_app_running():
        print("✅ 应用正在运行 (http://localhost:8527)")
    else:
        print("⚠️  应用可能未运行，请确保在另一个终端运行:")
        print("   conda activate writesong && python app.py --port 8527")
        response = input("\n是否继续运行测试? (y/n): ")
        if response.lower() != 'y':
            print("测试已取消")
            return
    
    # 定义测试列表
    tests = [
        {
            "name": "测试数据创建",
            "file": "create_test_data.py",
            "description": "创建测试用户和歌词数据"
        },
        {
            "name": "参考音频功能测试",
            "file": "test_ref_audio_fix.py", 
            "description": "验证参考音频上传和歌曲生成功能"
        },
        {
            "name": "离线功能测试",
            "file": "test_offline.py",
            "description": "测试离线模式和网络状态监控"
        }
    ]
    
    # 运行测试
    passed = 0
    total = len(tests)
    
    for test in tests:
        if os.path.exists(test["file"]):
            run_test(test["name"], test["file"], test["description"])
            passed += 1
        else:
            print(f"\n❌ 测试文件不存在: {test['file']}")
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    if passed == total:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    print(f"\n测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 