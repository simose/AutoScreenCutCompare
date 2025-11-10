import pytest
from playwright.sync_api import sync_playwright

from config.config import URLS, SCREENSHOTS_DIR
from pages.base_page import BasePage
from ScreenShot.screenshots import get_prefix_type


@pytest.mark.parametrize("url", URLS)
def test_take_full_page_screenshots(url):
    # 等待2秒：确保前次操作完成（对应需求中的操作步骤前等待）
    prefix_type = get_prefix_type()

    with sync_playwright() as p:
        # 等待2秒：启动浏览器前的缓冲
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        base_page = BasePage(page)

        # 等待2秒：页面导航前
        base_page.wait(2)
        print(f"\n🌐 正在访问: {url}")
        base_page.navigate(url)

        # 等待2秒：设置窗口大小前
        base_page.wait(2)
        base_page.maximize_window()

        # 等待2秒：处理弹窗前
        base_page.wait(2)
        base_page.close_popups()

        # 等待2秒：进行全页截图前
        base_page.wait(2)
        print(f"📸 开始截图，类型: {prefix_type}")
        base_page.take_full_page_screenshots(url, SCREENSHOTS_DIR, prefix_type)

        # 等待2秒：关闭浏览器前
        base_page.wait(2)
        browser.close()
        print(f"✅ 全页截图完成: {url}")

