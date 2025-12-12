# 测试URL配置
URLS = [
    "https://www.yunjiglobal.com/",
    "https://www.ankersolix.com/",
    "https://store.dji.com/",
    # "https://store.dji.com/product/dji-mic-3?vid=197721",
    "https://www.jackery.com/pages/about-us",
    "https://www.jackery.com/pages/news",
]

# 截图路径配置
SCREENSHOTS_DIR = "D:\\AutoScreenCut"

# 默认超时时间 (毫秒)
DEFAULT_TIMEOUT = 120000

# 是否使用整页截图模式 (True: 整页截图, False: 滚动截图)
USE_FULL_PAGE_SCREENSHOT = True

# 需要强制移除的弹窗选择器列表 (CSS选择器)
POPUP_SELECTORS = [
    # Jackery 公告栏
    # ".swiper-slide.announce-swiper-slide.announce-swiper-slide-1",
    ".announce-bar.announce-bar-show",
    # Klaviyo 营销弹窗 (特定版本)
    ".needsclick.klaviyo-form.klaviyo-form-version-cid_1.go3279073480.kl-private-reset-css-Xuajs1",
    # Klaviyo 通用匹配 (以防版本号变化)
    "[class*='klaviyo-form']",
    # 直播弹窗
    ".cy-player.needsclick",
    # 常见的 Cookie 同意横幅
    "#onetrust-banner-sdk",
    ".onetrust-pc-dark-filter",

    # ankersolix 公告栏
    ".Registrations_rsm_close_mask__LmRLM",
    ".RegistrationsModel_registrations_model__5DjjT",
    # # 关闭收集cookie弹窗标签内容
    # "[class^='cm__']",

    # 之前的通用关闭按钮选择器也可以作为补充，但这里主要放大的容器
    "div[role='dialog']",
    ".popup-container",
    ".modal-content"
]