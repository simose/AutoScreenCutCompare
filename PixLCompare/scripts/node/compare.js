import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

// 读取配置文件
function loadConfig() {
  try {
    const configPath = path.join(process.cwd(), 'config.json');
    const configData = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(configData);
  } catch (error) {
    console.error('❌ 读取配置文件失败:', error.message);
    console.log('使用默认配置...');
    return {
      imageDirectory: 'D:\\AutoScreenCut',
      filePatterns: {
        suffixA: '_A_',
        suffixB: '_B_',
        fileExtension: '.png'
      },
      comparison: {
        threshold: 1,
        includeAA: true,
        alpha: 1,
        diffMask: true,
        diffColor: [255, 0, 0],
        aaColor: [255, 255, 0]
      },
      output: {
        diffPrefix: 'diff_',
        generateDiffImages: true
      }
    };
  }
}

// 加载配置
const config = loadConfig();
const imageDir = config.imageDirectory;
const suffixA = config.filePatterns.suffixA;
const suffixB = config.filePatterns.suffixB;
const fileExtension = config.filePatterns.fileExtension;

// 扫描目录并找到匹配的图片对
function findMatchingImagePairs() {
  const files = fs.readdirSync(imageDir);
  const pairs = [];
  
  // 按前缀和序号分组
  const groupMap = new Map();
  
  files.forEach(file => {
    if (file.endsWith(fileExtension)) {
      // 动态匹配模式：支持两种格式
      // 格式1：前缀_A_序号.png (例如：jackery__A_001.png, 20250925_A_001.png)
      // 格式2：前缀A序号.png (例如：20250925A001.png, jackeryA001.png)
      let match = file.match(/^(.+)_([AB])_(\d+)\.png$/);
      if (!match) {
        match = file.match(/^(.+)([AB])(\d+)\.png$/);
      }
      
      if (match) {
        const [, prefix, type, number] = match;
        const key = `${prefix}_${number}`; // 使用前缀+序号作为唯一键
        
        if (!groupMap.has(key)) {
          groupMap.set(key, { prefix, number });
        }
        
        groupMap.get(key)[type] = file;
      }
    }
  });
  
  // 构建配对列表
  groupMap.forEach((data, key) => {
    if (data.A && data.B) {
      pairs.push({
        prefix: data.prefix,
        number: data.number,
        imgA: path.join(imageDir, data.A),
        imgB: path.join(imageDir, data.B)
      });
    }
  });
  
  // 按前缀和序号排序
  return pairs.sort((a, b) => {
    if (a.prefix !== b.prefix) {
      return a.prefix.localeCompare(b.prefix);
    }
    return parseInt(a.number) - parseInt(b.number);
  });
}

// 比较单对图片
function compareImagePair(pair) {
  console.log(`\n=== 比较图片对 [${pair.prefix}] ${pair.number} ===`);
  console.log(`图片A: ${path.basename(pair.imgA)}`);
  console.log(`图片B: ${path.basename(pair.imgB)}`);
  
  try {
    const img1 = PNG.sync.read(fs.readFileSync(pair.imgA));
    const img2 = PNG.sync.read(fs.readFileSync(pair.imgB));
    const { width, height } = img1;
    const diff = new PNG({ width, height });

    const numDiffPixels = pixelmatch(img1.data, img2.data, diff.data, width, height, {
      threshold: config.comparison.threshold,
      includeAA: config.comparison.includeAA,
      alpha: config.comparison.alpha,
      diffMask: config.comparison.diffMask,
      diffColor: config.comparison.diffColor,
      aaColor: config.comparison.aaColor,
    });

    console.log(`差异像素数：${numDiffPixels}`);

    // 只有当存在差异时才生成差异图片
    if (numDiffPixels > 0) {
      console.log('检测到差异，正在生成差异图片...');
      const outputPath = path.join(imageDir, `${config.output.diffPrefix}${pair.prefix}_${pair.number}.png`);
      
      // 如果差异图片已存在，先删除旧版本
      if (fs.existsSync(outputPath)) {
        fs.unlinkSync(outputPath);
        console.log(`已删除旧的差异图片: ${path.basename(outputPath)}`);
      }
      
      // 基于原图(第二张图)的拷贝，直接在图上标记差异像素
      const overlay = new PNG({ width, height });
      overlay.data.set(img2.data);
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const idx = (y * width + x) * 4;
          // diff 的 alpha 通道非 0 表示该像素存在差异
          if (diff.data[idx + 3] !== 0) {
            overlay.data[idx] = 255;     // R 红色高亮
            overlay.data[idx + 1] = 0;   // G
            overlay.data[idx + 2] = 0;   // B
            overlay.data[idx + 3] = 255; // A 不透明
          }
        }
      }
      fs.writeFileSync(outputPath, PNG.sync.write(overlay));
      console.log(`差异图片已保存到: ${outputPath}`);
      return { prefix: pair.prefix, number: pair.number, hasDiff: true, diffPixels: numDiffPixels, outputPath };
    } else {
      console.log('未检测到差异，跳过差异图片生成');
      return { prefix: pair.prefix, number: pair.number, hasDiff: false, diffPixels: 0 };
    }
  } catch (error) {
    console.error(`比较图片对 [${pair.prefix}] ${pair.number} 时出错:`, error.message);
    return { prefix: pair.prefix, number: pair.number, hasDiff: false, diffPixels: 0, error: error.message };
  }
}

// 主执行函数
function main() {
  console.log('🖼️ 开始扫描图片文件...');
  console.log('📋 当前配置:');
  console.log(`  扫描目录: ${imageDir}`);
  console.log(`  文件扩展名: ${fileExtension}`);
  console.log(`  比较阈值: ${config.comparison.threshold}`);
  console.log(`  差异图片前缀: ${config.output.diffPrefix}`);
  console.log('匹配模式:');
  console.log('  格式1: 任意前缀_A_序号.png 与 相同前缀_B_序号.png');
  console.log('  格式2: 任意前缀A序号.png 与 相同前缀B序号.png');
  
  const pairs = findMatchingImagePairs();
  
  if (pairs.length === 0) {
    console.log('❌ 未找到匹配的图片对');
    return;
  }
  
  console.log(`✅ 找到 ${pairs.length} 对匹配的图片`);
  
  // 按前缀分组显示
  const prefixGroups = {};
  pairs.forEach(pair => {
    if (!prefixGroups[pair.prefix]) {
      prefixGroups[pair.prefix] = [];
    }
    prefixGroups[pair.prefix].push(pair);
  });
  
  console.log('\n📋 发现的图片对分组:');
  Object.keys(prefixGroups).forEach(prefix => {
    console.log(`  前缀 "${prefix}": ${prefixGroups[prefix].length} 对`);
  });
  
  const results = [];
  pairs.forEach(pair => {
    const result = compareImagePair(pair);
    results.push(result);
  });
  
  // 输出总结
  console.log('\n=== 比较结果总结 ===');
  const withDiff = results.filter(r => r.hasDiff);
  const withoutDiff = results.filter(r => !r.hasDiff);
  
  console.log(`总比较对数: ${results.length}`);
  console.log(`有差异的对数: ${withDiff.length}`);
  console.log(`无差异的对数: ${withoutDiff.length}`);
  
  if (withDiff.length > 0) {
    console.log('\n有差异的图片对:');
    withDiff.forEach(r => {
      console.log(`  [${r.prefix}] 序号 ${r.number}: ${r.diffPixels} 个差异像素`);
    });
  }
  
  if (withoutDiff.length > 0) {
    console.log('\n无差异的图片对:');
    withoutDiff.forEach(r => {
      console.log(`  [${r.prefix}] 序号 ${r.number}: 完全一致`);
    });
  }
}

// 执行主函数
main();


