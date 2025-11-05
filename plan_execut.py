#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
import subprocess
from pathlib import Path


def ask_prefix_type(default_timeout_seconds: int = 20) -> str:
    """Ask for A/B type with timeout. Use env var PREFIX_TYPE if provided."""
    env_type = os.getenv("PREFIX_TYPE", "").strip().upper()
    if env_type in ["A", "B"]:
        print(f"✅ 从环境变量读取截图类型: {env_type}")
        return env_type

    user_input = [None]

    def read_input():
        try:
            user_input[0] = input().strip().upper()
        except (EOFError, KeyboardInterrupt):
            user_input[0] = None

    print(f"\n📝 请输入截图类型 (A 或 B)，{default_timeout_seconds}秒后自动选择 B:")
    t = threading.Thread(target=read_input, daemon=True)
    t.start()

    for remaining in range(default_timeout_seconds, 0, -1):
        if user_input[0] is not None:
            break
        print(f"\r⏰ 倒计时: {remaining} 秒 (输入 A 或 B，回车确认)...", end="", flush=True)
        time.sleep(1)

    print()

    if user_input[0] in ["A", "B"]:
        os.environ["PREFIX_TYPE"] = user_input[0]
        print(f"✅ 已设置截图类型为: {user_input[0]}")
        return user_input[0]

    print("⏰ 倒计时结束或输入无效，自动选择 B")
    os.environ["PREFIX_TYPE"] = "B"
    return "B"


def run_tests() -> bool:
    """Run pytest for screenshot tests."""
    project_dir = Path(__file__).parent
    cmd = [sys.executable, "-m", "pytest", "ScreenShot/screenshots.py", "-v", "-s"]
    try:
        print("\n🚀 开始执行测试...\n📋 执行命令:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=project_dir)
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("🎉 测试执行成功！")
            return True
        print("❌ 测试执行失败！\n返回码:", result.returncode)
        return False
    except Exception as e:
        print(f"❌ 执行测试时出错: {e}")
        return False


def run_compare() -> bool:
    """Run PixLCompare node-based compare via Python wrapper."""
    project_dir = Path(__file__).parent
    compare_script = project_dir / "PixLCompare" / "run_compare.py"
    if not compare_script.exists():
        print(f"❌ 找不到图片比较脚本: {compare_script}")
        return False
    try:
        result = subprocess.run([sys.executable, str(compare_script)], capture_output=False, text=True, cwd=project_dir)
        if result.returncode == 0:
            print("✅ 图片比较执行成功！")
            return True
        print(f"❌ 图片比较执行失败！返回码: {result.returncode}")
        return False
    except Exception as e:
        print(f"❌ 执行图片比较时出错: {e}")
        return False


