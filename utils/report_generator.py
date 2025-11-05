import os
import datetime
from config.config import SCREENSHOTS_DIR, REPORTS_DIR

def generate_html_report(screenshots_dir=None, reports_dir=None):
    # 使用配置的默认路径
    if screenshots_dir is None:
        screenshots_dir = SCREENSHOTS_DIR
    if reports_dir is None:
        reports_dir = REPORTS_DIR
        
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    today = datetime.date.today().strftime("%Y-%m-%d")
    report_filename = os.path.join(reports_dir, f"report_{today}.html")

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Screenshot Report</title></head><body>")
        f.write(f"<h1>Screenshot Report - {today}</h1>")

        # 直接扫描截图目录中的PNG文件
        if os.path.exists(screenshots_dir):
            png_files = [f for f in os.listdir(screenshots_dir) if f.endswith(".png")]
            if png_files:
                f.write("<h2>所有截图</h2>")
                for file in sorted(png_files):
                    screenshot_path = os.path.join(screenshots_dir, file)
                    # 使用相对路径作为HTML报告中的图像源
                    relative_screenshot_path = os.path.relpath(screenshot_path, reports_dir)
                    f.write(f'<img src="{relative_screenshot_path}" width="500"><br>')
                    f.write(f'<p>文件: {file}</p><br>')
            else:
                f.write("<p>未找到截图文件</p>")
        else:
            f.write("<p>截图目录不存在</p>")

        f.write("</body></html>")

    print(f"Report generated: {report_filename}")