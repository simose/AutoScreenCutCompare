#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI自动化测试执行脚本
使用Python + Playwright框架进行网站截图测试
"""

import os
import sys
import subprocess
import time
import argparse
import threading
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("           UI自动化测试执行器")
    print("         Python + Playwright 框架")
    print("=" * 60)
    print()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UI 自动化截图与对比执行器")
    parser.add_argument("--type", choices=["A", "B"], help="截图类型：A 仅截图；B 截图后执行对比")
    parser.add_argument("--skip-compare", action="store_true", help="跳过图片对比（即使选择了 B）")
    return parser.parse_args()

def check_virtual_env():
    """检查是否在虚拟环境中（可选，不强制要求）"""
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ 检测到虚拟环境已激活")
    else:
        print("⚠️  未检测到虚拟环境（建议使用虚拟环境，但不强制要求）")
    return True  # 不强制要求虚拟环境，只做提示

def check_dependencies():
    """检查必要的依赖包"""
    required_packages = ['pytest', 'playwright']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n需要安装的包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        if 'playwright' in missing_packages:
            print("playwright install chromium")
        return False
    
    return True

def check_playwright_browsers():
    """检查Playwright浏览器是否安装"""
    try:
        result = subprocess.run(['playwright', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Playwright 浏览器已安装")
            return True
        else:
            print("❌ Playwright 浏览器未安装")
            print("请运行: playwright install chromium")
            return False
    except Exception as e:
        print(f"❌ 检查Playwright浏览器时出错: {e}")
        return False

def create_screenshot_dir():
    """创建截图目录（从配置文件读取）"""
    try:
        from config.config import SCREENSHOTS_DIR
        screenshot_dir = SCREENSHOTS_DIR
    except ImportError:
        # 如果配置文件不存在，使用默认路径
        screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        print(f"⚠️  无法读取配置文件，使用默认路径: {screenshot_dir}")
    
    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        print(f"✅ 截图目录已准备: {screenshot_dir}")
        return True
    except Exception as e:
        print(f"❌ 创建截图目录失败: {e}")
        return False

def check_pixlcompare_env():
    """检查 PixLCompare 运行环境（Node.js 和依赖）"""
    project_dir = Path(__file__).parent
    pixlcompare_dir = project_dir / "PixLCompare"
    
    # 检查 PixLCompare 目录是否存在
    if not pixlcompare_dir.exists():
        print("⚠️  PixLCompare 目录不存在，图片比较功能将不可用")
        return True  # 不强制要求，因为 A 类型不需要
    
    # 检查 Node.js 是否安装
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✅ Node.js 已安装: {node_version}")
        else:
            print("❌ Node.js 未正确安装")
            print("请安装 Node.js: https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ Node.js 未安装或未添加到 PATH")
        print("请安装 Node.js: https://nodejs.org/")
        print("安装后需要重启终端或重新加载环境变量")
        return False
    except Exception as e:
        print(f"❌ 检查 Node.js 时出错: {e}")
        return False
    
    # 检查 package.json 是否存在
    package_json = pixlcompare_dir / "package.json"
    if not package_json.exists():
        print("⚠️  PixLCompare/package.json 不存在，图片比较功能可能不可用")
        return True  # 不强制要求
    
    # 检查 node_modules 是否存在
    node_modules = pixlcompare_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  PixLCompare 依赖未安装")
        print("请运行以下命令安装依赖:")
        print(f"  cd {pixlcompare_dir}")
        print("  npm ci")
        return False
    
    # 检查关键脚本文件是否存在
    compare_script = pixlcompare_dir / "scripts" / "node" / "compare.js"
    if not compare_script.exists(): # 检查关键脚本文件是否存在
        print(f"⚠️  找不到图片比较脚本: {compare_script}")
        return False
    
    print("✅ PixLCompare 环境检查通过")
    return True

from plan_execut import ask_prefix_type, run_tests, run_compare

# 使用 plan_execut 中的实现

def main():
    """主函数"""
    print_banner()
    args = parse_args()
    
    # 检查环境
    print("🔍 检查运行环境...")
    if not check_virtual_env():
        print("❌ 虚拟环境检查失败，请手动激活虚拟环境后重试")
        return 1
    
    if not check_dependencies():
        print("❌ 依赖包检查失败，请安装必要的包后重试")
        return 1
    
    if not check_playwright_browsers():
        print("❌ Playwright浏览器检查失败，请安装浏览器后重试")
        return 1
    
    
    # 检查 PixLCompare 环境（可选，仅在 B 类型时需要）
    if not check_pixlcompare_env():
        print("⚠️  PixLCompare 环境检查失败，如果选择 B 类型可能无法执行图片比较")
    
    print("\n✅ 环境检查完成，所有依赖都已就绪！")
    
    # 获取截图类型（参数优先，其次环境变量/交互）
    if args.type:
        os.environ["PREFIX_TYPE"] = args.type
        prefix_type = args.type
        print(f"✅ 从参数读取截图类型: {prefix_type}")
    else:
        prefix_type = ask_prefix_type()
    
    # 如果选择 B 类型，再次检查 PixLCompare 环境
    if prefix_type == 'B' and not args.skip_compare:
        print("\n🔍 重新检查 PixLCompare 环境（B 类型需要图片比较功能）...")
        if not check_pixlcompare_env():
            print("❌ PixLCompare 环境检查失败，无法执行图片比较")
            user_confirm = input("是否继续执行截图（将跳过图片比较）？(y/n): ").strip().lower()
            if user_confirm != 'y':
                print("已取消执行")
                return 1
    
    # 运行测试
    success = run_tests()
    
    # 显示结果
    print("\n" + "=" * 60)
    if success:
        print("🎊 所有测试已完成！")
        try:
            from config.config import SCREENSHOTS_DIR
            print(f"📸 截图已保存到: {SCREENSHOTS_DIR}")
        except ImportError:
            print("📸 截图已保存")
        
        # 根据用户输入的类型决定是否执行图片比较
        if prefix_type == 'B' and not args.skip_compare:
            print(f"\n📝 检测到截图类型为 B，将执行图片比较...")
            compare_success = run_compare()
            if not compare_success:
                print("⚠️ 图片比较执行失败，但截图测试已完成")
        elif prefix_type == 'A':
            print(f"\n📝 检测到截图类型为 A，跳过图片比较")
        else:
            print(f"\n⚠️ 无法确定截图类型，跳过图片比较")
    else:
        print("💥 测试执行过程中出现错误")
    
    print("=" * 60)
    # 自动退出，不等待用户输入
    print("\n⏰ 3秒后自动退出...")
    time.sleep(3)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)
