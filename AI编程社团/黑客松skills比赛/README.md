# 公众号爆款内容创作系统

每天5分钟，AI帮你写爆款公众号文章！

## 功能特点

- 🔥 自动采集多平台热点（微博、知乎、抖音）
- 🤖 AI智能写文章，保留你的个人风格
- 📋 一键复制到剪贴板，直接粘贴发布
- 📁 本地保存文章历史，随时查看

## 安装

1. 安装 Python 3.10 或更高版本

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 配置 API 密钥：

打开 `config.py` 文件，填写你的 API 密钥：

```python
# 选择AI服务: "openai" 或 "claude"
AI_PROVIDER = "openai"

# OpenAI API Key
OPENAI_API_KEY = "sk-your-key-here"

# 或者 Claude API Key
# CLAUDE_API_KEY = "sk-ant-your-key-here"
```

## 使用方法

运行主程序：
```bash
python main.py
```

### 操作流程

1. **获取热点**：选择 "1"，系统会自动获取微博、知乎、抖音的热门话题

2. **写文章**：选择 "2"，从热点中选择一个话题，AI会自动为你生成一篇完整的公众号文章

3. **发布文章**：文章会自动复制到剪贴板，打开公众号后台粘贴即可发布

4. **历史管理**：选择 "3" 或 "4" 查看和管理历史文章

## 项目结构

```
.
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── spiders/               # 爬虫模块
│   ├── weibo_spider.py   # 微博热搜
│   ├── zhihu_spider.py   # 知乎热榜
│   └── douyin_spider.py  # 抖音热门
├── services/              # 业务服务
│   ├── hot_topic_service.py
│   ├── ai_writer.py
│   └── article_service.py
├── storage/               # 数据存储
│   └── db.py
└── output/               # 输出文章
    └── articles/
```

## 注意事项

1. 热点平台可能反爬，建议设置合理的请求间隔
2. AI生成的文章建议人工审核后再发布
3. 遵守平台规则，合理使用爬虫

## 常见问题

**Q: 抓不到热点怎么办？**
A: 检查网络连接，或者热点平台的网页结构是否变化

**Q: AI文章太长/太短？**
A: 修改 config.py 中的 ARTICLE_WORD_COUNT 参数

**Q: 如何修改写作风格？**
A: 修改 config.py 中的 WRITING_STYLE 配置

---

祝你公众号阅读量飙升！ 🚀
