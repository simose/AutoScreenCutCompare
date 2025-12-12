import os
import datetime
from urllib.parse import urlparse
import json
from playwright.sync_api import Page
from config.config import USE_FULL_PAGE_SCREENSHOT, DEFAULT_TIMEOUT, POPUP_SELECTORS

class BasePage:
    """基础页面封装
    提供导航、窗口管理、等待、弹窗关闭与页面截图等通用方法。
    适用于基于 Playwright 的同步 API 场景。
    """
    def __init__(self, page: Page):
        """初始化页面对象并设置默认超时时间

        参数:
            page: Playwright 的 `Page` 实例
        """
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT)
        self.inject_auto_popup_remover()

    def inject_auto_popup_remover(self):
        """注入 JS 脚本以自动移除配置的弹窗元素
        
        利用 page.add_init_script 在页面加载前注入脚本，
        并使用 MutationObserver 持续监控 DOM 变化，一旦发现匹配的弹窗元素即刻移除。
        """
        selectors_json = json.dumps(POPUP_SELECTORS)
        js_script = f"""
            const popupSelectors = {selectors_json};
            
            function removePopups() {{
                popupSelectors.forEach(selector => {{
                    try {{
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {{
                            // 移除元素
                            el.remove();
                            console.log('Auto-removed popup:', selector);
                        }});
                    }} catch (e) {{
                        // 忽略选择器错误
                    }}
                }});
            }}

            // 1. 初始执行
            if (document.body) removePopups();

            // 2. 定时检查 (每 500ms)
            setInterval(removePopups, 500);

            // 3. MutationObserver 监听 DOM 变化
            const observer = new MutationObserver((mutations) => {{
                let shouldCheck = false;
                for (const mutation of mutations) {{
                    if (mutation.addedNodes.length > 0) {{
                        shouldCheck = true;
                        break;
                    }}
                }}
                if (shouldCheck) removePopups();
            }});
            
            // 等待 body 加载后开始监听
            const startObserver = () => {{
                if (document.body) {{
                    observer.observe(document.body, {{ childList: true, subtree: true }});
                    removePopups();
                }} else {{
                    requestAnimationFrame(startObserver);
                }}
            }};
            
            startObserver();
            
            // 监听 load 事件作为额外保险
            window.addEventListener('load', removePopups);
        """
        self.page.add_init_script(js_script)

    def remove_configured_popups(self):
        """手动触发一次弹窗移除 (JS)
        
        在截图等关键操作前调用，确保视口干净。
        """
        selectors_json = json.dumps(POPUP_SELECTORS)
        self.page.evaluate(f"""
            const selectors = {selectors_json};
            selectors.forEach(selector => {{
                try {{
                    document.querySelectorAll(selector).forEach(el => el.remove());
                }} catch (e) {{}}
            }});
        """)

    def navigate(self, url: str):
        """跳转到指定的 `url`"""
        self.page.goto(url)

    def maximize_window(self):
        """设置浏览器视口为 1920x1080，以便统一截图尺寸"""
        self.page.set_viewport_size({"width": 1920, "height": 1080})

    def wait(self, seconds: int):
        """显式等待指定秒数"""
        self.page.wait_for_timeout(seconds * 1000)

    def close_popups(self):
        """尝试关闭页面上的常见弹窗/模态框

        通过一组通用选择器检测是否可见并点击关闭按钮，避免阻挡后续操作。
        """
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
                # 若选择器定位到的元素可见，则点击关闭并稍作等待
                if self.page.locator(selector).is_visible():
                    self.page.locator(selector).click()
                    self.page.wait_for_timeout(500)
            except Exception:
                # 某些页面不存在对应元素或不可交互，忽略异常继续尝试下一个选择器
                pass

    def take_full_page_screenshots(self, url: str, output_dir: str, prefix_type: str):
        """页面截图（全页或分段）

        根据配置 `USE_FULL_PAGE_SCREENSHOT` 选择：
        - 全页截图：一次性保存整页
        - 分段截图：按滚动位置逐段截图直到页面底部

        另外根据 `url` 生成文件名前缀，输出至 `output_dir`。

        参数:
            url: 当前页面的 URL，用于生成文件名前缀
            output_dir: 截图输出目录，不存在时会创建
            prefix_type: 前缀类型标识，如 `expected`/`actual` 等
        """
        if not os.path.exists(output_dir):
            # 若输出目录不存在则创建
            os.makedirs(output_dir)

        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            prefix = "homepage"
        else:
            prefix = path.split("/")[-1].replace("-", "_")

        # 截图前先进行一次手动清理
        self.remove_configured_popups()

        if USE_FULL_PAGE_SCREENSHOT:
            # 1. 先执行滚动预加载逻辑
            previous_scroll_position = -1
            current_scroll_position = 0
            scroll_count = 0
            max_scroll_count = 100  # 防止无限滚动，最大滚动100次
            
            print(f"开始全页截图预加载滚动: {url}")
            while current_scroll_position != previous_scroll_position and scroll_count < max_scroll_count:
                # 滚动到当前目标位置
                self.page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
                # 每次滚动后等待 1000ms 让内容加载
                self.page.wait_for_timeout(1000)
                # 尝试清理弹窗
                self.remove_configured_popups()

                previous_scroll_position = current_scroll_position
                current_scroll_position = self.page.evaluate("window.innerHeight + window.scrollY")
                page_height = self.page.evaluate("document.body.scrollHeight")
                
                scroll_count += 1
                if scroll_count % 5 == 0:
                     print(f"  - 正在滚动... ({int(current_scroll_position)}/{int(page_height)}px)")
                
                if current_scroll_position >= page_height:
                    current_scroll_position = page_height
                    if previous_scroll_position == current_scroll_position:
                        break
            
            if scroll_count >= max_scroll_count:
                print(f"⚠️ 达到最大滚动次数限制 ({max_scroll_count})，停止滚动预加载。")

            # 2. 滚动到底部后，额外等待 5 秒确保所有懒加载资源完成 
            self.wait(5)
            
            # 3. 滚回到顶部
            self.page.evaluate("window.scrollTo(0, 0)")
            
            # 4. 再次清理确保万无一失
            self.remove_configured_popups() 
            
            # 5. 执行全页截图
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
            # 使用滚动位置控制分段截图
            previous_scroll_position = -1
            current_scroll_position = 0

            while current_scroll_position != previous_scroll_position:
                # 滚动到当前目标位置并等待内容渲染稳定
                self.page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
                self.page.wait_for_timeout(3000)
                
                # 每次滚动后都尝试清理弹窗
                self.remove_configured_popups()

                screenshot_name = f"{prefix}_{prefix_type}_{screenshot_count:03d}.png"
                screenshot_path = os.path.join(output_dir, screenshot_name)
                # 进行当前视口截图
                self.page.screenshot(path=screenshot_path, full_page=False)
                print(f"截图已保存: {screenshot_path}")

                previous_scroll_position = current_scroll_position
                # 计算下一次滚动位置（当前视口底部）
                current_scroll_position = self.page.evaluate("window.innerHeight + window.scrollY")
                
                # 获取页面整体高度，用于判断是否到达底部
                page_height = self.page.evaluate("document.body.scrollHeight")
                if current_scroll_position >= page_height:
                    current_scroll_position = page_height
                    if previous_scroll_position == current_scroll_position:
                        break
                
                screenshot_count += 1
