#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// Assumes repository layout:
// - root/AI编程社团/微博热搜分析/weibo_product_260119.html
// - root/AI编程社团/微博热搜分析/weibo_product_260121.html
// Outputs to root/weibo_product_260119.html and root/weibo_product_260121.html

const root = path.resolve(__dirname, '..');
const src119 = path.resolve(root, 'AI编程社团', '微博热搜分析', 'weibo_product_260119.html');
const src121 = path.resolve(root, 'AI编程社团', '微博热搜分析', 'weibo_product_260121.html');
const dst119 = path.resolve(root, 'weibo_product_260119.html');
const dst121 = path.resolve(root, 'weibo_product_260121.html');

function generateAll(){
  if(!fs.existsSync(src119) || !fs.existsSync(src121)){
    console.error('Source templates not found. Ensure 260119/260121 HTMLs exist in AI编程社团/微博热搜分析.');
    process.exit(2);
  }
  const c119 = fs.readFileSync(src119, 'utf8');
  const c121 = fs.readFileSync(src121, 'utf8');
  // Write to root outputs
  fs.writeFileSync(dst119, c119, 'utf8');
  fs.writeFileSync(dst121, c121, 'utf8');
  console.log('Generated:');
  console.log(' - ' + dst119);
  console.log(' - ' + dst121);
}

function main(){
  const arg = process.argv[2];
  if(!arg || arg === 'all' || arg === 'both'){
    generateAll();
  } else {
    console.log('Usage: node scripts/generate_weibo_reports.js [all|both]');
  }
}

main();
