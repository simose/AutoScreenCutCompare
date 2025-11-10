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
  
  // 使用更灵活的匹配策略：只要A和B类型的文件前缀和后缀完全相等就匹配
  const groupMap = new Map();
  
  files.forEach(file => {
    if (file.endsWith(fileExtension)) {
      // 查找文件名中的A或B标识
      const aMatch = file.match(/^(.+)A(.+)\.png$/);
      const bMatch = file.match(/^(.+)B(.+)\.png$/);
      
      if (aMatch) {
        // A类型文件
        const [, prefix, suffix] = aMatch;
        const key = `${prefix}_${suffix}`; // 使用前缀+后缀作为唯一键
        
        if (!groupMap.has(key)) {
          groupMap.set(key, { prefix, suffix, aFile: null, bFile: null });
        }
        groupMap.get(key).aFile = file;
      } else if (bMatch) {
        // B类型文件
        const [, prefix, suffix] = bMatch;
        const key = `${prefix}_${suffix}`; // 使用前缀+后缀作为唯一键
        
        if (!groupMap.has(key)) {
          groupMap.set(key, { prefix, suffix, aFile: null, bFile: null });
        }
        groupMap.get(key).bFile = file;
      }
    }
  });
  
  // 构建配对列表
  groupMap.forEach((data, key) => {
    if (data.aFile && data.bFile) {
      pairs.push({
        prefix: data.prefix,
        suffix: data.suffix,
        key: key,
        imgA: path.join(imageDir, data.aFile),
        imgB: path.join(imageDir, data.bFile)
      });
    }
  });
  
  // 按前缀和后缀排序
  return pairs.sort((a, b) => {
    if (a.prefix !== b.prefix) {
      return a.prefix.localeCompare(b.prefix);
    }
    return a.suffix.localeCompare(b.suffix);
  });
}

// 比较单对图片
function compareImagePair(pair) {
  console.log(`\n=== 比较图片对 [${pair.prefix}] ${pair.suffix} ===`);
  console.log(`图片A: ${path.basename(pair.imgA)}`);
  console.log(`图片B: ${path.basename(pair.imgB)}`);
  
  try {
    const img1 = PNG.sync.read(fs.readFileSync(pair.imgA));
    const img2 = PNG.sync.read(fs.readFileSync(pair.imgB));
    
    // 检查图片尺寸是否匹配
    if (img1.width !== img2.width || img1.height !== img2.height) {
      console.log(`⚠️ 图片尺寸不匹配: A图 ${img1.width}x${img1.height}, B图 ${img2.width}x${img2.height}`);
      console.log('跳过此对比对');
      return { prefix: pair.prefix, suffix: pair.suffix, hasDiff: false, diffPixels: 0, error: '尺寸不匹配' };
    }
    
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
      const outputPath = path.join(imageDir, `${config.output.diffPrefix}${pair.prefix}_${pair.suffix}.png`);
      
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
      return { prefix: pair.prefix, suffix: pair.suffix, hasDiff: true, diffPixels: numDiffPixels, outputPath };
    } else {
      console.log('未检测到差异，跳过差异图片生成');
      return { prefix: pair.prefix, suffix: pair.suffix, hasDiff: false, diffPixels: 0 };
    }
  } catch (error) {
    console.error(`比较图片对 [${pair.prefix}] ${pair.suffix} 时出错:`, error.message);
    return { prefix: pair.prefix, suffix: pair.suffix, hasDiff: false, diffPixels: 0, error: error.message };
  }
}

// 主函数
function main() {
  console.log('开始图片对比...');
  console.log(`图片目录: ${imageDir}`);
  console.log(`差异图片前缀: ${config.output.diffPrefix}`);
  
  const pairs = findMatchingImagePairs();
  
  if (pairs.length === 0) {
    console.log('未找到可对比的图片对，请确保图片命名格式正确。');
    console.log('支持的格式：');
    console.log('1. 任意前缀_A_任意后缀.png 与 相同前缀_B_相同后缀.png');
    console.log('2. 例如：homepage_A_full.png vs homepage_B_full.png');
    console.log('3. 例如：test_A_001.png vs test_B_001.png');
    console.log('4. 例如：long_prefix_A_123.png vs long_prefix_B_123.png');
    return;
  }
  
  console.log(`\n找到 ${pairs.length} 对可对比的图片`);
  
  const results = [];
  let totalDiffPixels = 0;
  let pairsWithDiff = 0;
  
  for (const pair of pairs) {
    const result = compareImagePair(pair);
    results.push(result);
    
    if (result.hasDiff) {
      pairsWithDiff++;
      totalDiffPixels += result.diffPixels;
    }
  }
  
  // 输出统计结果
  console.log('\n=== 对比完成 ===');
  console.log(`总对比对数: ${pairs.length}`);
  console.log(`有差异的对数: ${pairsWithDiff}`);
  console.log(`无差异的对数: ${pairs.length - pairsWithDiff}`);
  console.log(`总差异像素数: ${totalDiffPixels}`);
  
  // 输出详细结果
  console.log('\n=== 详细结果 ===');
  results.forEach(result => {
    if (result.error) {
      console.log(`❌ [${result.prefix}] ${result.suffix}: ${result.error}`);
    } else if (result.hasDiff) {
      console.log(`🔍 [${result.prefix}] ${result.suffix}: 发现 ${result.diffPixels} 个差异像素`);
    } else {
      console.log(`✅ [${result.prefix}] ${result.suffix}: 无差异`);
    }
  });
  
  // 如果有差异，输出差异图片信息
  const diffResults = results.filter(r => r.hasDiff && !r.error);
  if (diffResults.length > 0) {
    console.log('\n=== 差异图片 ===');
    diffResults.forEach(result => {
      console.log(`🔴 ${path.basename(result.outputPath)}`);
    });
  }
}

// 执行主函数
main();


