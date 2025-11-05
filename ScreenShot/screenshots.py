import os
import pytest
from playwright.sync_api import sync_playwright
from pages.base_page import BasePage
from config.config import URLS, SCREENSHOTS_DIR

# 全局变量存储用户输入的A/B类型
PREFIX_TYPE = None

def get_prefix_type():
    """优先从环境变量读取 A/B；未设置时再交互式输入（仅一次）。"""
    global PREFIX_TYPE
    if PREFIX_TYPE is not None:
        return PREFIX_TYPE

    env_type = os.getenv("PREFIX_TYPE", "").strip().upper()
    if env_type in ["A", "B"]:
        PREFIX_TYPE = env_type
        print(f"✅ 从环境变量读取截图类型: {PREFIX_TYPE}")
        return PREFIX_TYPE

    while True:
        prefix_type = input("请输入截图类型 (A 或 B): ").strip().upper()
        if prefix_type in ['A', 'B']:
            PREFIX_TYPE = prefix_type
            print(f"✅ 已设置截图类型为: {PREFIX_TYPE}")
            break
        else:
            print("❌ 输入无效，请输入 A 或 B")
    return PREFIX_TYPE

@pytest.mark.parametrize("url", URLS)
def test_take_screenshots(url):
    # 获取用户输入的A/B变量（全局共享）
    prefix_type = get_prefix_type()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Set headless=False to see the browser
        page = browser.new_page()
        base_page = BasePage(page)

        print(f"\n🌐 正在访问: {url}")
        base_page.navigate(url)
        base_page.maximize_window()
        base_page.wait(2)  # 等待2秒
        base_page.close_popups()

        print(f"📸 开始截图，类型: {prefix_type}")
        base_page.take_full_page_screenshots(url, SCREENSHOTS_DIR, prefix_type)

        browser.close()
        print(f"✅ 页面截图完成: {url}")