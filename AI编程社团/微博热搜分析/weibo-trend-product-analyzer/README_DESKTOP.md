# 微博热搜AI产品分析助手 (桌面版)

这是一个基于Python Tkinter开发的桌面应用程序，集成了微博热搜API和简单的AI分析逻辑（模拟）。

## 功能特点
- 实时获取微博热搜榜单
- 自动分析热搜背后的产品创意
- 生成HTML分析报告
- 图形化界面，操作简单

## 运行方式

### 1. 直接运行源码
确保已安装Python 3.x，然后在终端运行：

```bash
pip install -r requirements.txt
python gui_main.py
```

### 2. 打包为EXE文件
如果你想生成可独立运行的EXE文件，请运行：

```bash
python build_exe.py
```
打包完成后，可在 `dist` 目录下找到 `WeiboAI_Assistant.exe`。

## 依赖库
- requests (如果analyzer.py使用了)
- pyinstaller (用于打包)
- tkinter (Python内置)
