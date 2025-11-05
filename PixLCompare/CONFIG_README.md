# 配置文件说明

## 概述

本项目现在使用统一的配置文件 `config.json` 来管理所有配置参数，避免了之前路径不一致的问题。

## 配置文件结构

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

## 配置项说明

### imageDirectory
- **类型**: 字符串
- **说明**: 图片文件所在的目录路径
- **示例**: `"D:\\AutoScreenCut"`

### filePatterns
包含文件匹配相关的配置：

- **suffixA**: A组图片的后缀标识符
- **suffixB**: B组图片的后缀标识符  
- **fileExtension**: 支持的文件扩展名

### comparison
包含图片比较算法的参数：

- **threshold**: 比较阈值 (0.0-1.0)，越小越敏感
- **includeAA**: 是否包含抗锯齿检测
- **alpha**: 透明度阈值
- **diffMask**: 是否生成差异遮罩
- **diffColor**: 差异像素的RGB颜色值
- **aaColor**: 抗锯齿像素的RGB颜色值

### output
包含输出相关的配置：

- **diffPrefix**: 差异图片的文件名前缀
- **generateDiffImages**: 是否生成差异图片

## 使用方法

### 1. 修改配置
直接编辑 `config.json` 文件中的相应值即可。

### 2. 运行程序
```bash
# 使用Python运行器（推荐）
python run_compare.py

# 或直接运行Node.js脚本
node pixelmatch/test/compare.js
```

### 3. 测试配置
```bash
python test_config.py
```

## 支持的图片命名格式

程序支持以下两种命名格式：

1. **格式1**: `前缀_A_序号.png` 与 `前缀_B_序号.png`
   - 示例: `jackery_A_001.png`, `jackery_B_001.png`

2. **格式2**: `前缀A序号.png` 与 `前缀B序号.png`
   - 示例: `jackeryA001.png`, `jackeryB001.png`

## 故障排除

### 配置文件不存在
如果程序提示找不到配置文件，请确保 `config.json` 文件存在于项目根目录。

### 图片目录不存在
如果提示找不到图片目录，请检查 `imageDirectory` 路径是否正确，或创建相应的目录。

### 配置格式错误
如果JSON格式有误，程序会显示具体错误信息，请检查JSON语法。

## 优势

1. **统一管理**: 所有配置集中在一个文件中
2. **避免冲突**: 消除了路径不一致的问题
3. **易于维护**: 修改配置无需修改代码
4. **向后兼容**: 配置文件不存在时会使用默认配置
5. **详细日志**: 显示当前使用的配置信息
