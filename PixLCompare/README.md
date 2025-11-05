## PixLCompare

轻量级的本地图片差异对比工具，基于 pixelmatch（Node.js）完成像素级比较，并提供 Python 启动器与统一配置文件，适合批量 UI 截图回归对比与差异可视化。

### 功能特性
- **统一配置**: 使用根目录 `config.json` 管理图片目录、命名规则与比较参数。
- **像素级对比**: 基于 pixelmatch，支持阈值、AA 检测、遮罩颜色等细粒度调优。
- **批量处理**: 自动按命名规则配对 A/B 图，生成差异图。
- **即开即用**: `python run_compare.py` 一键执行对比；`test_config.py` 快速校验配置可用性。

### 目录结构
```
PixLCompare/
├── README.md
├── CONFIG_README.md
├── package.json               # 管理 pixelmatch、pngjs 依赖
├── config.json                # 统一配置
├── diff_coords.json           # 差异坐标（可选）
├── run_compare.py             # Python 启动器（推荐入口）
└── scripts/
    └── node/
        └── compare.js         # 实际执行的对比脚本
```

### 环境依赖
- Node.js（用于运行 pixelmatch 脚本）
- Python 3.8+（用于统一启动与校验配置）

可选：如需手动安装/升级 pixelmatch，可在 `pixelmatch/` 中使用 npm，但本仓库已内置可用版本。

### 快速开始
1) 修改根目录 `config.json`，至少确认图片目录与命名规则：
```json
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

2) 运行配置自检（可选）：
```bash
python test_config.py
```

3) 执行图片对比（推荐入口）：
```bash
python run_compare.py
```

成功后将在 `imageDirectory` 指定目录内输出以 `diffPrefix` 命名的差异图（如 `diff_*.png`）。

### 图片命名与配对规则
支持以下两种常见命名（可按需扩展）：
- 格式1：`<前缀>_A_<序号>.png` 与 `<前缀>_B_<序号>.png`
  - 示例：`jackery_A_001.png`、`jackery_B_001.png`
- 格式2：`<前缀>A<序号>.png` 与 `<前缀>B<序号>.png`

通过 `filePatterns.suffixA / suffixB / fileExtension` 进行灵活适配。

function diffTest(imgPath1, imgPath2, diffPath, options, expectedMismatch)

*   imgPath1, imgPath2 — 需要比较的图像数据。注意：   图像尺寸必须相等。
*   output — 输出差异图像的数据，或如果不需要差异图像则为 null。
*   width, height —   图像的宽度和高度。注意，所有三张图像 都需要有相同的尺寸。 options 是一个具有以下属性的对象字面量：

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

*   threshold — 匹配阈值，范围从 0 到 1。较小的值会使比较更敏感。默认为 0.1。注意：测试发现效果并不佳）
*   includeAA — 如果为 true，则禁用检测并忽略抗锯齿像素。默认为 false。
*   alpha — 差异输出中未更改像素的混合因子。范围从 0（纯白色）到   1（原始亮度）。默认为 0.1。
*   aaColor — 差异输出中抗锯齿像素的颜色，格式为 \[R, G, B]。默认为 \[255, 255,0]。
*   diffColor — 差异输出中不同像素的颜色，格式为 \[R, G, B]。默认为 \[255, 0, 0]。
*   diffColorAlt — 用于区分明暗差异的替代颜色，以区分“添加”和“移除”的部分。如果未提供，所有不同像素使用 diffColor指定的颜色。默认为 null。
*   diffMask — 在透明背景（遮罩）上绘制差异，而不是在原始图像上绘制。将不会绘制检测到的抗锯齿像素。比较两张图像，写入输出差异，并返回不匹配像素的数量。


### 常用脚本
- `python run_compare.py`：读取 `config.json` 并调用 `pixelmatch/test/compare.js` 批量对比。
- `python test_config.py`：检查配置文件存在性、JSON 正确性与关键字段。
- `node pixelmatch/test/compare.js`：直接调用 Node 脚本（需已正确配置路径）。

### 常见问题排查
- 配置文件不存在：确认 `config.json` 位于项目根目录。
- 图片目录不存在：检查 `imageDirectory` 路径是否正确或先行创建。
- JSON 解析失败：按提示修正 JSON 语法（逗号、引号、数组等）。
- 未生成差异图：
  - 确认 A/B 文件命名匹配；
  - 调高/调低 `comparison.threshold`；
  - 确认 `output.generateDiffImages = true`；
  - 检查 `diffPrefix` 与输出目录是否一致。

### 进一步说明
- 更详细的参数释义与使用示例见 `CONFIG_README.md`。
- 需要将工具融入 CI/CD 时，建议固定 Node 与 Python 版本，并在流水线中执行 `python run_compare.py`。

### 许可证
本项目内置并使用开源库 pixelmatch（遵循其各自许可）。除非另行声明，本项目以 MIT 许可开源。


