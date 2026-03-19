#!/usr/bin/env node

/**
 * Claude Slash Commands CLI
 * 通用型斜杠命令 - 任何目录都可调用
 */

const { Command } = require('commander');
const chalk = require('chalk');
const inquirer = require('inquirer');

const program = new Command();

program
  .name('claude-slash')
  .description('Claude 通用斜杠命令工具')
  .version('1.0.0');

// 命令映射表
const COMMANDS = {
  a: { name: 'analyze', desc: '代码分析', prompt: '请描述你想要分析的内容：' },
  b: { name: 'build', desc: '项目构建', prompt: '请输入构建命令（直接回车使用默认）：' },
  c: { name: 'commit', desc: 'Git 提交', prompt: '请描述你的变更：' },
  d: { name: 'docs', desc: '文档生成', prompt: '请描述需要生成的文档类型：' },
  g: { name: 'generate', desc: '代码生成', prompt: '请描述需要生成的内容：' },
  r: { name: 'review', desc: '代码审查', prompt: '请描述需要审查的范围：' },
  s: { name: 'search', desc: '代码搜索', prompt: '请输入搜索关键词：' },
  t: { name: 'test', desc: '测试运行', prompt: '请输入测试命令（直接回车使用默认）：' },
  w: { name: 'weibo', desc: '微博热搜分析', prompt: '请输入热搜主题（直接回车使用默认）：' },
  x: { name: 'fix', desc: '问题修复', prompt: '请描述遇到的问题或错误：' },
  z: { name: 'ai', desc: 'AI 助手', prompt: '请输入你的问题：' }
};

// 动态注册命令
Object.entries(COMMANDS).forEach(([key, info]) => {
  program
    .command(key)
    .alias(info.name)
    .description(info.desc)
    .action(async () => {
      console.log(chalk.blue(`\n🚀 正在启动 ${info.desc}...\n`));

      const { input } = await inquirer.prompt([
        {
          type: 'input',
          name: 'input',
          message: info.prompt,
          default: ''
        }
      ]);

      // 输出提示信息，告诉用户如何在 Claude Code 中使用
      console.log(chalk.green(`\n✅ 输入已记录: ${input || '（空）'}`));
      console.log(chalk.yellow(`\n💡 提示: 在 Claude Code 中直接使用 /${key} 命令可以获得更好的体验\n`));
    });
});

// 显示帮助
program.on('--help', () => {
  console.log(chalk.cyan('\n可用命令：'));
  Object.entries(COMMANDS).forEach(([key, info]) => {
    console.log(`  /${key} 或 ${info.name.padEnd(8)} ${info.desc}`);
  });
  console.log(chalk.cyan('\n示例：'));
  console.log(`  claude-slash a        # 启动代码分析`);
  console.log(`  claude-slash w        # 微博热搜分析\n`);
});

program.parse();
