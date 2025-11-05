import os
import datetime
import time
from urllib.parse import urlparse
from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    def maximize_window(self):
        """
        最大化当前浏览器窗口。
        通过设置大分辨率（1920x1080）实现，保证页面元素完整展示，提升脚本兼容性和稳定性。
        """
        self.page.set_viewport_size({"width": 1920, "height": 1080})

    def wait(self, seconds: int):
        """
        等待指定毫秒数。

        """
        self.page.wait_for_timeout(seconds * 1000)

    def close_popups(self):
        """
        自动检测并关闭常见网站弹窗（如Cookie、弹窗广告、提醒等）。
        增强用例的健壮性，避免弹窗影响后续自动化步骤。
        可根据实际测试项目需要补充选择器。
        """
        selectors = [
            'button:has-text("Close")',
            'button[aria-label="Close"]',
            'div[role="dialog"] button:has-text("No thanks")',
            '#onetrust-accept-btn-handler', # Common cookie consent button
            '.close-button',
            '.popup-close',
            '.modal-close'
        ]
        for selector in selectors:
            try:
                if self.page.locator(selector).is_visible():
                    self.page.locator(selector).click()
                    self.page.wait_for_timeout(500) # short wait for popup to disappear
            except Exception:
                pass

    def take_full_page_screenshots(self, url: str, output_dir: str, prefix_type: str):
        """
        滚动并逐屏截取当前页面，保存为连续编号的 PNG 图片。

        步骤：
            1. 校验并创建输出目录。
            2. 根据URL生成文件名前缀，便于区分不同页面截图。
            3. 循环滚动页面直至底部，对每一屏内容依次截图，文件名自动递增编号。
            4. 支持对已有同类图片批量清理，保证本次截图编号连续。
        """
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成基于URL的前缀（仅区分首页与最低层级）
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            prefix = "homepage"
        else:
            prefix = path.split("/")[-1].replace("-", "_")

        # 清理相同前缀和类型的现有截图以重新开始编号
        try:
            for filename in os.listdir(output_dir):
                if filename.startswith(f"{prefix}_{prefix_type}_") and filename.endswith(".png"):
                    file_path = os.path.join(output_dir, filename)
                    os.remove(file_path)
            print(f"清理完成：已移除 {prefix}_{prefix_type}_*.png 旧文件")
        except Exception as e:
            print(f"清理旧文件时出错：{e}")

        screenshot_count = 1
        previous_scroll_position = -1
        current_scroll_position = 0

        while current_scroll_position != previous_scroll_position:
            # Scroll to the current position
            self.page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
            self.page.wait_for_timeout(1000)  # Wait for scroll and content to load

            # 生成截图名称，格式：prefix_A/B_001
            screenshot_name = f"{prefix}_{prefix_type}_{screenshot_count:03d}.png"
            screenshot_path = os.path.join(output_dir, screenshot_name)
            self.page.screenshot(path=screenshot_path, full_page=False)  # 截取可见部分
            print(f"截图已保存: {screenshot_path}")

            previous_scroll_position = current_scroll_position
            # Scroll down to the next section
            current_scroll_position = self.page.evaluate("window.innerHeight + window.scrollY")
            
            # Check if we are at the bottom of the page
            page_height = self.page.evaluate("document.body.scrollHeight")
            if current_scroll_position >= page_height:
                current_scroll_position = page_height # Ensure we don't scroll past the end
                if previous_scroll_position == current_scroll_position:
                    break # Reached the bottom and no more scrolling possible
            
            screenshot_count += 1