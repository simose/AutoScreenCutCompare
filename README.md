## AutoScreenCutCompare - UI自动化截图与图像对比

### 项目简介

基于 Python + Playwright 的 UI 自动化截图工具，采用 PO 模式（Page Object Model）。支持 A/B 两套截图方案，并在 B 流程完成后自动调用像素级图片对比（Node.js + pixelmatch）。

*

### 实战结果比对

[案例1](https://github.com/mapbox/pixelmatch/issues/127)（从源码问题中复制来的）：
图A001
![请添加图片描述](https://i-blog.csdnimg.cn/direct/d78d0f7314f642208eb72afc8625f188.png)
图B001
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d46fd10fa7a044dabdc701b6c9954d27.png)
B对于基准A的对比结果
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2c227c199c23450e867433bc0e462b6f.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/43d09182384947a2a063d9ee140f5f57.png)

对比结果日志输出
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/eaf69496d0e4496381d2f4c3feff8b6b.png)

### 项目落地过程中存在的问题

​
吸顶变换的滚动条
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/1aaff8d8a5974f598425e363cbfba9c9.png)

动态变化-倒计时
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b969f6788fd54af7a64a686a711e971f.png)

预加载的弹窗
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6a5e478db97349d3a8392a5d36e83b57.png)

动态的动画效果
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/74342fc9d9424a5ba694fca01e59a7e4.png)


### 关键特性

- **PO 模式**：`pages/base_page.py` 封装页面操作，代码清晰易维护
- **多 URL 批量测试**：从 `config/config.py` 读取 URL 列表
- **滚动分屏截图**：自动连续编号保存，命名清晰
- **A/B 流程控制**：
  - 输入 A：仅截图，不做对比
  - 输入 B：截图完成后执行 `PixLCompare/run_compare.py` 进行对比
- **2秒操作节拍**：每步操作前预留等待（在测试/页面操作中实现）
 

### 目录结构（当前）

```
AutoScreenCutCompare/
├── config/
│   ├── __init__.py
│   └── config.py              # URL配置和截图目录配置
├── pages/
│   ├── __init__.py
│   └── base_page.py           # 页面操作基类（PO模式）
├── ScreenShot/
│   ├── __init__.py
│   └── screenshots.py         # pytest测试用例
├── utils/
│   ├── __init__.py
│   └── report_generator.py    # 报告生成工具
├── PixLCompare/
│   ├── config.json            # 图片对比配置
│   ├── diff_coords.json       # 差异坐标记录
│   ├── package.json           # Node.js依赖配置
│   ├── package-lock.json      # 依赖锁定文件
│   ├── README.md              # PixLCompare模块说明
│   ├── CONFIG_README.md       # 配置说明文档
│   ├── run_compare.py         # 图片对比执行脚本
│   └── scripts/
│       └── node/
│           └── compare.js     # Node.js图片对比脚本
├── env_checks.py              # 环境检查模块（虚拟环境、依赖、浏览器等）
├── Plan_execut.py             # 执行计划模块（A/B类型选择、测试执行、对比执行）
├── run_auto_screen_cut.py     # 主执行脚本（一键运行入口）
└── README.md
```

### 环境要求

- Python 3.9+
- Node.js 16+
- Playwright + 浏览器内核
- pytest
- 虚拟环境：`D:\Cursor\UK0519\.venv`

### 安装与初始化

1) 激活虚拟环境（固定路径）
```
***.venv\Scripts\activate
```

2) 安装 Python 依赖
```
pip install pytest playwright
```

3) 安装 Playwright 浏览器
```
playwright install chromium
```

4) 安装对比脚本依赖（可选，用于 B 流程图像对比）
```
cd PixLCompare
npm ci   # 或 npm install
```

### 配置

编辑 `config/config.py`：
```python
# 测试URL配置
URLS = [
    "https://www.yunjiglobal.com/",
]

# 截图保存目录
SCREENSHOTS_DIR = "D:\\AutoScreenCut"
```

如需自定义对比输出与阈值，配置 `PixLCompare/config.json`。

### 使用方法

#### 方法一：一键运行（推荐）

命令行执行：
```
python run_auto_screen_cut.py
```

或使用命令行参数：
```
python run_auto_screen_cut.py --type B        # 直接指定类型为B
python run_auto_screen_cut.py --type A        # 直接指定类型为A
python run_auto_screen_cut.py --type B --skip-compare  # B类型但跳过对比
```

流程：
1. **环境检查**（`env_checks.py`）：
   - 检查虚拟环境状态
   - 检查Python依赖包（pytest、playwright）
   - 检查Playwright浏览器安装
   - 检查截图目录
   - 检查PixLCompare环境（Node.js、npm依赖，仅B类型需要）

2. **获取截图类型**（`Plan_execut.py` 的 `ask_prefix_type`）：
   - 优先从命令行参数 `--type` 读取
   - 其次从环境变量 `PREFIX_TYPE` 读取
   - 未设置则交互式输入（20秒倒计时，默认选择B）

3. **执行截图测试**（`Plan_execut.py` 的 `run_tests`）：
   - 运行 `pytest ScreenShot/screenshots.py -v -s`
   - 截图保存到配置的目录

4. **执行图片对比**（仅B类型，`Plan_execut.py` 的 `run_compare`）：
   - 自动调用 `PixLCompare/run_compare.py` 完成像素对比
   - 生成差异图（前缀见 `PixLCompare/config.json` 的 `output.diffPrefix`）

说明：可通过多种方式传递A/B类型：
```
# 方式1：命令行参数（推荐）
python run_auto_screen_cut.py --type B

# 方式2：环境变量
set PREFIX_TYPE=B && python run_auto_screen_cut.py  # Windows CMD
$env:PREFIX_TYPE="B"; python run_auto_screen_cut.py  # PowerShell

# 方式3：交互式输入（20秒倒计时）
python run_auto_screen_cut.py
```

**📊PixLCompare**：
function diffTest(imgPath1, imgPath2, diffPath, options, expectedMismatch)

 - imgPath1, imgPath2 — 需要比较的图像数据。注意：   图像尺寸必须相等。 
 - output — 输出差异图像的数据，或如果不需要差异图像则为 null。 
 - width, height —   图像的宽度和高度。注意，所有三张图像 都需要有相同的尺寸。 options 是一个具有以下属性的对象字面量：   
 
 ```python
 {
  "imageDirectory": "D:\\AutoScreenCut",
  "filePatterns": {
    "suffixA": "_A_",
    "suffixB": "_B_",
    "fileExtension": ".png"
  },
  "comparison": {
    "threshold": 0.1,
    "includeAA": true,
    "alpha": 1,
    "diffMask": true,
    "diffColor": [255, 0, 0],
    "aaColor": [255, 255, 0]
  },
  "output": {
    "diffPrefix": "diff_",
    "generateDiffImages": true
  }
}
```
  - threshold — 匹配阈值，范围从 0 到 1。较小的值会使比较更敏感。默认为 0.1。注意：测试发现效果并不佳）
  - includeAA — 如果为 true，则禁用检测并忽略抗锯齿像素。默认为 false。
  - alpha — 差异输出中未更改像素的混合因子。范围从 0（纯白色）到   1（原始亮度）。默认为 0.1。 
  - aaColor — 差异输出中抗锯齿像素的颜色，格式为 [R, G, B]。默认为 [255, 255,0]。 
  - diffColor — 差异输出中不同像素的颜色，格式为 [R, G, B]。默认为 [255, 0, 0]。
  - diffColorAlt — 用于区分明暗差异的替代颜色，以区分“添加”和“移除”的部分。如果未提供，所有不同像素使用 diffColor指定的颜色。默认为 null。
  - diffMask — 在透明背景（遮罩）上绘制差异，而不是在原始图像上绘制。将不会绘制检测到的抗锯齿像素。比较两张图像，写入输出差异，并返回不匹配像素的数量。


#### 方法二：直接运行 pytest

```
pytest ScreenShot/screenshots.py -v -s
```

注意：直接运行pytest时，需要手动设置环境变量 `PREFIX_TYPE` 或通过交互式输入选择A/B类型。

### 截图与命名规则

- 主页：`homepage_{A|B}_001.png`
- 其他页面：使用 URL 最低层级路径（`-` → `_`），如 `solar_generator_A_001.png`
- 每屏递增编号：`_001.png`, `_002.png`, ...

### A/B 流程说明（重要）

- **类型A（基准截图）**：
  - 仅执行截图，保存为 `*_A_*.png` 格式
  - 跳过像素对比
  - 用于建立基准图片

- **类型B（对比截图）**：
  - 执行截图，保存为 `*_B_*.png` 格式
  - 截图完成后，自动调用 `PixLCompare/run_compare.py`
  - 基于 `pixelmatch` 对比A/B图片，生成差异图（前缀见 `PixLCompare/config.json` 的 `output.diffPrefix`）
  - 差异图保存为 `diff_*.png` 格式

- **获取类型的方式**（优先级从高到低）：
  1. 命令行参数：`--type A` 或 `--type B`
  2. 环境变量：`PREFIX_TYPE=A` 或 `PREFIX_TYPE=B`
  3. 交互式输入：20秒倒计时，默认选择B

### 设计与实现要点

- **`pages/base_page.py`**（PO模式基类）：
  - `navigate`、`maximize_window`、`close_popups` 封装常用操作
  - `take_full_page_screenshots` 实现滚动分屏截图与文件清理
  - `wait(seconds)` 提供节拍等待（测试中统一以 2s 为基准）

- **`ScreenShot/screenshots.py`**（pytest测试用例）：
  - 使用 `@pytest.mark.parametrize` 批量测试多个URL
  - 从环境变量 `PREFIX_TYPE` 或交互式输入获取A/B类型
  - 每个URL执行完整的截图流程

- **`Plan_execut.py`**（执行计划模块）：
  - `ask_prefix_type`：获取A/B类型（支持命令行参数、环境变量、交互式输入）
  - `run_tests`：执行pytest测试
  - `run_compare`：执行图片对比（B类型时调用）

- **`env_checks.py`**（环境检查模块）：
  - `check_virtual_env`：检查虚拟环境
  - `check_dependencies`：检查Python依赖
  - `check_playwright_browsers`：检查Playwright浏览器
  - `create_screenshot_dir`：创建截图目录
  - `check_pixlcompare_env`：检查Node.js和PixLCompare依赖

- **`run_auto_screen_cut.py`**（主执行脚本）：
  - 环境检查（调用 `env_checks.py`）
  - 获取截图类型（调用 `Plan_execut.ask_prefix_type`）
  - 执行测试（调用 `Plan_execut.run_tests`）
  - B类型时执行对比（调用 `Plan_execut.run_compare`）

### 常见问题（FAQ）

1) Playwright 提示未安装浏览器
- 执行：`playwright install chromium`

2) Node.js 对比步骤报错
- 确认已在 `PixLCompare/` 安装依赖：`npm ci`
- 确认已安装 Node，并在 PATH 中可用

 

4) 截图未生成或数量异常
- 检查 `config/config.py` 的 `SCREENSHOTS_DIR` 是否存在/可写
- 某些长页需适当增加等待/滚动节拍

### 约定与路径
 
- 截图输出目录：`D:\AutoScreenCut`

---

如需二次开发，可在 `pages/` 扩展页面操作，在 `ScreenShot/` 添加用例，或在 `PixLCompare/` 调整像素对比逻辑与配置。
