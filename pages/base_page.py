import os
import datetime
from urllib.parse import urlparse
from playwright.sync_api import Page
from config.config import USE_FULL_PAGE_SCREENSHOT, DEFAULT_TIMEOUT

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT)

    def navigate(self, url: str):
        self.page.goto(url)

    def maximize_window(self):
        self.page.set_viewport_size({"width": 1920, "height": 1080})

    def wait(self, seconds: int):
        self.page.wait_for_timeout(seconds * 1000)

    def close_popups(self):
        selectors = [
            'button:has-text("Close")',
            'button[aria-label="Close"]',
            'div[role="dialog"] button:has-text("No thanks")',
            '#onetrust-accept-btn-handler',
            '.close-button',
            '.popup-close',
            '.modal-close'
        ]
        for selector in selectors:
            try:
                if self.page.locator(selector).is_visible():
                    self.page.locator(selector).click()
                    self.page.wait_for_timeout(500)
            except Exception:
                pass

    def take_full_page_screenshots(self, url: str, output_dir: str, prefix_type: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            prefix = "homepage"
        else:
            prefix = path.split("/")[-1].replace("-", "_")

        if USE_FULL_PAGE_SCREENSHOT:
            self.wait(2)
            screenshot_name = f"{prefix}_{prefix_type}_full.png"
            screenshot_path = os.path.join(output_dir, screenshot_name)
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"全页截图已保存: {screenshot_path}")
        else:
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
                self.page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
                self.page.wait_for_timeout(1000)

                screenshot_name = f"{prefix}_{prefix_type}_{screenshot_count:03d}.png"
                screenshot_path = os.path.join(output_dir, screenshot_name)
                self.page.screenshot(path=screenshot_path, full_page=False)
                print(f"截图已保存: {screenshot_path}")

                previous_scroll_position = current_scroll_position
                current_scroll_position = self.page.evaluate("window.innerHeight + window.scrollY")
                
                page_height = self.page.evaluate("document.body.scrollHeight")
                if current_scroll_position >= page_height:
                    current_scroll_position = page_height
                    if previous_scroll_position == current_scroll_position:
                        break
                
                screenshot_count += 1