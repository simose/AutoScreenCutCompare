#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片比较脚本运行器
自动执行 pixelmatch 图片比较功能
"""

import subprocess
import os
import sys
import json
from pathlib import Path

def load_config():
    """
    加载配置文件
    """
    try:
        current_dir = Path(__file__).parent.absolute()
        config_path = current_dir / "config.json"
        
        if not config_path.exists():
            print(f"❌ 错误: 找不到配置文件 {config_path}")
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print(f"✅ 成功加载配置文件: {config_path}")
        return config
        
    except Exception as e:
        print(f"❌ 加载配置文件失败: {str(e)}")
        return None

def run_image_compare():
    """
    运行图片比较脚本
    """
    try:
        # 加载配置文件
        config = load_config()
        if config is None:
            return False
            
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent.absolute()
        print(f"当前工作目录: {current_dir}")
        
        # 检查 compare.js 文件是否存在（迁移后路径）
        compare_script = current_dir / "scripts" / "node" / "compare.js"
        if not compare_script.exists():
            print(f"❌ 错误: 找不到文件 {compare_script}")
            return False
        
        print(f"✅ 找到脚本文件: {compare_script}")
        
        # 从配置文件获取图片目录
        img_dir = config["imageDirectory"]
        if not os.path.exists(img_dir):
            print(f"❌ 错误: 找不到图片目录 {img_dir}")
            print("请检查配置文件中的 imageDirectory 路径是否正确")
            return False
        
        print(f"✅ 找到图片目录: {img_dir}")

        # 在比较前删除旧的差异图片
        try:
            diff_prefix = config["output"]["diffPrefix"]
            deleted_count = 0
            # 支持的图片扩展名
            valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
            
            for filename in os.listdir(img_dir):
                if filename.startswith(diff_prefix) and filename.lower().endswith(valid_extensions):
                    file_path = os.path.join(img_dir, filename)
                    os.remove(file_path)
                    deleted_count += 1
            if deleted_count > 0:
                print(f"🧹 清理完成: 删除了 {deleted_count} 个旧的差异图片。")
                print("📋 支持的对比格式:")
                print("   - 滚动截图: 前缀_A_序号.png vs 前缀_B_序号.png")
                print("   - 全屏截图: 前缀_A_full.png vs 前缀_B_full.png")
        except Exception as e:
            print(f"⚠️ 清理旧差异文件时出错: {e}")
        
        # 执行 Node.js 脚本
        print("\n🚀 开始执行图片比较...")
        print("=" * 50)
        
        result = subprocess.run(
            ["node", str(compare_script)],
            cwd=current_dir,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 输出结果
        if result.stdout:
            print("📊 执行结果:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误信息:")
            print(result.stderr)
        
        # 检查执行状态
        if result.returncode == 0:
            print("✅ 脚本执行成功!")
            
            # 检查是否有差异图片生成（扫描配置前缀开头的文件）
            diff_prefix = config["output"]["diffPrefix"]
            diff_files = []
            # 支持的图片扩展名
            valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
            
            for file in os.listdir(img_dir):
                if file.startswith(diff_prefix) and file.lower().endswith(valid_extensions):
                    diff_files.append(os.path.join(img_dir, file))
            
            if diff_files:
                print(f"✅ 生成了 {len(diff_files)} 个差异图片:")
                for diff_file in diff_files:
                    print(f"   - {diff_file}")
            else:
                print("ℹ️ 未检测到差异，未生成差异图片")
            
            return True
        else:
            print(f"❌ 脚本执行失败，退出码: {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ 错误: 找不到 Node.js，请确保已安装 Node.js 并添加到 PATH")
        return False
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {str(e)}")
        return False

def main():
    """
    主函数：执行图片对比
    
    支持格式（只要前缀和后缀相同即可对比）：
    1. 任意前缀_A_任意后缀.png vs 相同前缀_B_相同后缀.png
    2. 例如：
       - homepage_A_full.png vs homepage_B_full.png (全屏截图)
       - test_A_001.png vs test_B_001.png (滚动截图)
       - long_prefix_A_123.png vs long_prefix_B_123.png
       - 01_A_001.png vs 01_B_001.png
    
    对比前会自动删除旧的差异图片文件
    """
    print("🖼️ 图片比较脚本运行器")
    print("=" * 50)
    
    success = run_image_compare()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 任务完成!")
    else:
        print("💥 任务失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
