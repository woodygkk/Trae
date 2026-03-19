# 🚀 快速入门指南

5分钟开始使用AI News Skill！

## Step 1: 安装依赖 (1分钟)

```bash
cd ~/.claude/skills/ai-news
bash setup.sh
```

这会自动：
- ✅ 安装Python依赖
- ✅ 创建必要目录
- ✅ 初始化数据库
- ✅ 获取第一批新闻

## Step 2: 查看新闻 (30秒)

```bash
cd ~/.claude/skills/ai-news
python3 scripts/ai_news.py today
```

你应该能看到类似这样的输出：

```markdown
# 🤖 AI Today's Top News

**Date**: 2026-03-03 14:30
**Articles**: 10

---

## 🔥 Top 1: OpenAI Releases GPT-5...
...
```

## Step 3: 配置推送 (3分钟)

### 选择一个推送渠道

#### 方案A: 飞书（最推荐）

1. **创建飞书机器人**
   - 打开飞书群聊
   - 右上角 `⋮` → 设置 → 机器人
   - 添加机器人 → 自定义机器人
   - 名称: "AI资讯助手"
   - 复制Webhook URL

2. **配置Webhook**

编辑 `config/push.yaml`:

```yaml
feishu:
  enabled: true
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/粘贴你的TOKEN"
```

3. **测试推送**

```bash
python3 scripts/ai_news.py push
```

检查你的飞书群，应该收到了新闻推送！

#### 方案B: 企业微信

```yaml
wechat_work:
  enabled: true
  webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的KEY"
```

#### 方案C: 邮件

```yaml
email:
  enabled: true
  to: "your-email@example.com"
```

## Step 4: 设置自动推送 (可选)

### 方式1: 使用内置调度器

```bash
# 在后台持续运行
nohup python3 scripts/scheduler.py > scheduler.log 2>&1 &
```

调度器会：
- 每小时自动更新新闻
- 每天早上8点推送（可在push.yaml修改时间）

### 方式2: 使用systemd（Linux推荐）

创建服务文件 `/etc/systemd/system/ai-news.service`:

```ini
[Unit]
Description=AI News Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/.claude/skills/ai-news
ExecStart=/usr/bin/python3 scripts/scheduler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable ai-news
sudo systemctl start ai-news
sudo systemctl status ai-news
```

## 常用命令速查

```bash
# 查看今日新闻
python3 scripts/ai_news.py today

# 查看Top 20
python3 scripts/ai_news.py today --count 20

# 按分类筛选
python3 scripts/ai_news.py today --category 技术突破

# 更新新闻数据库
python3 scripts/ai_news.py update

# 推送到配置的渠道
python3 scripts/ai_news.py push

# 查看统计信息
python3 scripts/ai_news.py stats
```

## 🎯 推荐使用场景

### 场景1: 个人每日晨读
- 每天早上8点自动推送到手机（飞书/Telegram）
- 5分钟快速浏览当日Top 10

### 场景2: 团队信息共享
- 推送到团队飞书群
- 全员及时了解AI行业动态

### 场景3: 深度研究
- 启用arXiv论文源
- 筛选"研究论文"分类
- 追踪最新学术进展

## ❓ 常见问题

### Q: 没有看到新闻？
A: 先运行 `python3 scripts/ai_news.py update` 更新数据库

### Q: 推送失败？
A: 检查 `config/push.yaml` 中的Webhook URL是否正确

### Q: 想添加更多新闻源？
A: 编辑 `config/sources.yaml`，添加RSS feed URL

### Q: 如何修改推送时间？
A: 编辑 `config/push.yaml` 中的 `schedule.daily_time`

## 🔧 进阶定制

### 自定义评分算法
编辑 `scripts/process.py` 中的 `calculate_article_score()` 函数

### 自定义分类规则
编辑 `scripts/process.py` 中的 `CATEGORIES` 字典

### 添加新的推送渠道
编辑 `scripts/push.py`，参考现有渠道实现

## 📚 更多帮助

- 完整文档: `README.md`
- 详细调研报告: 查看workspace中的调研文档
- 问题反馈: 联系开发者

---

**就这么简单！** 享受你的AI资讯助手吧 🎉
