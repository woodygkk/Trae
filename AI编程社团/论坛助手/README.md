# 链接转换工具

帮助用户将论坛内容迁移过程中的超链接一键转换为目标平台的链接。

## 快速开始

### 网页版（立即可用）

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

构建完成后，在浏览器中打开 `dist/index.html` 即可使用。

### 桌面客户端（需要编译环境）

Windows 环境需要安装 Visual Studio Build Tools 才能编译 Tauri 桌面应用。

```bash
# 安装 Rust（如果未安装）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 编译桌面应用
npm run tauri build
```

## 功能特性

- 支持 HTML/富文本和纯文本格式
- 实时预览转换结果
- 域名配置灵活可保存
- 一键复制转换结果

## 技术栈

- React + TypeScript
- Vite
- Tauri（桌面客户端）

## 目录结构

```
论坛助手/
├── src/
│   ├── components/      # React 组件
│   │   ├── ConfigPanel.tsx
│   │   ├── InputPanel.tsx
│   │   └── OutputPanel.tsx
│   ├── core/            # 核心逻辑
│   │   ├── linkConverter.ts
│   │   └── configManager.ts
│   ├── App.tsx          # 主应用
│   └── App.css          # 样式
├── src-tauri/           # Tauri 后端
├── dist/                # 构建输出
├── Prd.md               # 产品需求文档
└── package.json
```
