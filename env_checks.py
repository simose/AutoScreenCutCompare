#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from pathlib import Path


def check_virtual_env() -> bool:
    """Check if running inside a virtual environment (non-blocking)."""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ 检测到虚拟环境已激活")
    else:
        print("⚠️  未检测到虚拟环境（建议使用虚拟环境，但不强制要求）")
    return True


def check_dependencies() -> bool:
    """Check required Python packages are installed."""
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
        print("请运行以下命令安装 (优先使用阿里云镜像):")
        print(f"pip install {' '.join(missing_packages)} -i https://mirrors.aliyun.com/pypi/simple")
        if 'playwright' in missing_packages:
            print("# 安装浏览器内核（使用国内镜像源，加速下载）")
            print("$env:PLAYWRIGHT_DOWNLOAD_HOST='https://npmmirror.com/mirrors/playwright'  # PowerShell")
            print("set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright  # CMD")
            print("playwright install chromium")
        return False

    return True


def check_playwright_browsers() -> bool:
    """Check if Playwright browsers are installed (CLI available)."""
    try:
        result = subprocess.run(['playwright', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Playwright 浏览器已安装")
            return True
        else:
            print("❌ Playwright 浏览器未安装")
            print("请运行 (使用国内镜像源):")
            print("$env:PLAYWRIGHT_DOWNLOAD_HOST='https://npmmirror.com/mirrors/playwright'; playwright install chromium  # PowerShell")
            print("set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright && playwright install chromium  # CMD")
            return False
    except Exception as e:
        print(f"❌ 检查Playwright浏览器时出错: {e}")
        return False


def create_screenshot_dir() -> bool:
    """Ensure screenshot directory exists (from config)."""
    try:
        from config.config import SCREENSHOTS_DIR
        screenshot_dir = SCREENSHOTS_DIR
    except ImportError:
        screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        print(f"⚠️  无法读取配置文件，使用默认路径: {screenshot_dir}")

    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        print(f"✅ 截图目录已准备: {screenshot_dir}")
        return True
    except Exception as e:
        print(f"❌ 创建截图目录失败: {e}")
        return False


def check_pixlcompare_env() -> bool:
    """Check Node.js and PixLCompare dependencies."""
    project_dir = Path(__file__).parent
    pixlcompare_dir = project_dir / "PixLCompare"

    if not pixlcompare_dir.exists():
        print("⚠️  PixLCompare 目录不存在，图片比较功能将不可用")
        return True  # optional when using A-type only

    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
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

    package_json = pixlcompare_dir / "package.json"
    if not package_json.exists():
        print("⚠️  PixLCompare/package.json 不存在，图片比较功能可能不可用")
        return True

    node_modules = pixlcompare_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  PixLCompare 依赖未安装")
        print("请运行以下命令安装依赖（使用阿里云 npm 镜像）:")
        print(f"  cd {pixlcompare_dir}")
        print("  npm config set registry https://registry.npmmirror.com")
        print("  npm ci")
        return False

    compare_script = pixlcompare_dir / "scripts" / "node" / "compare.js"
    if not compare_script.exists():
        print(f"⚠️  找不到图片比较脚本: {compare_script}")
        return False

    print("✅ PixLCompare 环境检查通过")
    return True


