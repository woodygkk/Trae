---
name: weibo-trend-product-analyzer
description: "微博热搜产品创意分析工具。自动抓取微博热搜榜单，搜索热点背景信息，AI分析提取产品创意，生成HTML分析报告。评分标准：有趣度80% + 有用度20%。评级：优秀(>80分)、良好(60-80分)、普通(<60分)。"
license: MIT
---

# 微博热搜产品创意分析

## 概述

本技能用于分析微博热搜榜单，从热点事件中提取有价值的产品创意。通过自动化抓取、搜索、分析和报告生成，帮助产品经理和创业者快速发现市场机会。

## API配置

**API端点**：
```
https://apis.tianapi.com/weibohot/index?key=55560316d6858702ce84f6748c277d14
```

**API响应格式**（天行数据微博热搜API）：
```json
{
  "code": 200,
  "msg": "success",
  "result": {
    "list": [
      {
        "hotword": "热搜话题标题",
        "hotwordnum": "热度数值（字符串，带空格分隔）",
        "hottag": "话题标签"
      }
    ]
  }
}
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| hotword | string | 热搜话题标题 |
| hotwordnum | string | 热度数值，需转换为整数 |
| hottag | string | 话题标签分类 |

## 使用场景

- 产品经理寻找新功能灵感
- 创业者寻找市场切入点
- 运营人员策划热点营销
- 投资人调研市场趋势

## 输入格式

用户可以使用以下方式调用：

```
分析微博热搜产品创意
使用微博热搜创意分析
```

可选参数：
- `top_n`：分析的热搜数量（默认10条）
- `output_path`：输出HTML报告路径（默认 weibo_product_ideas.html）

## 工作流程

### 步骤1：抓取微博热搜榜单

使用天行数据API获取微博热搜数据：
```
GET https://apis.tianapi.com/weibohot/index?key=xxx
```

解析响应中的 `result.list` 数组，提取：
- `hotword`：热搜话题标题（注意：不是word）
- `hotwordnum`：热度指数（字符串格式，需转换为整数）
- `hottag`：话题标签

**数据处理示例**：
```python
hotword = topic.get("hotword", "")
heat_str = topic.get("hotwordnum", "0").replace(" ", "").replace(",", "")
heat = int(heat_str)  # 转换为整数
```

### 步骤2：搜索热点背景信息

对每个热搜话题，使用WebSearch工具搜索：
- 相关新闻报道和事件进展
- 事件背景和发展脉络
- 社交媒体讨论焦点
- 专家观点和用户评论

### 步骤3：AI分析与产品创意提取

对每个热点进行深度分析，从以下维度评估：

**评分标准（总分100分）**：

| 维度 | 权重 | 评估要点 |
|------|------|----------|
| 有趣度 | 80% | 创新性、吸引力、传播潜力、话题热度 |
| 有用度 | 20% | 商业可行性、用户需求、市场空间 |

**产品创意输出格式**：
```json
{
  "topic": "热搜话题",
  "product_name": "产品名称（简洁有力）",
  "core_features": ["核心功能1", "核心功能2", "核心功能3"],
  "target_users": "目标用户群体描述",
  "interesting_score": 0-80,
  "usefulness_score": 0-20,
  "total_score": 0-100,
  "rating": "优秀|良好|普通",
  "reason": "评分理由和产品创意说明"
}
```

**产品创意匹配规则**：

| 关键词 | 产品名称 | 核心功能 |
|--------|---------|---------|
| AI、人工智能、大模型、ChatGPT | AI助手Pro | 多模型切换、智能对话、文档生成、代码辅助 |
| 手机、苹果、华为、小米 | 手机评测精选 | 对比工具、价格追踪、参数查询、购买建议 |
| 电影、电视剧、综艺、追剧 | 追剧助手 | 更新提醒、资源聚合、评分对比、观影清单 |
| 游戏、王者、原神、吃鸡 | 游戏攻略盒子 | 攻略查询、战绩分析、社区讨论、礼包领取 |
| 教育、学习、考试、考研、公务员 | 考试助手 | 题库练习、错题本、学习计划、院校查询 |
| 美食、吃、餐厅、外卖、食谱 | 美食发现 | 餐厅推荐、食谱教程、热量计算、美食打卡 |
| 旅游、旅行、景点、酒店 | 旅行规划师 | 行程规划、景点推荐、预算计算、游记分享 |
| 汽车、新能源、特斯拉、比亚迪 | 汽车点评 | 车型对比、价格查询、口碑查看、贷款计算 |
| 电商、购物、省钱、优惠 | 省线购物 | 比价工具、优惠推送、返利汇总、好物推荐 |
| 健身、运动、减肥、瑜伽、跑步 | 健身私教 | 训练计划、饮食记录、进度追踪、社区打卡 |

### 步骤4：生成HTML分析报告

生成结构化的HTML报告，包含：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>微博热搜产品创意分析报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 20px;
            text-align: center;
        }
        .excellent { border-left: 6px solid #10b981; background: linear-gradient(to right, #ecfdf5, white); }
        .good { border-left: 6px solid #3b82f6; background: linear-gradient(to right, #eff6ff, white); }
        .normal { border-left: 6px solid #9ca3af; background: #fafafa; }
        .score-badge {
            padding: 8px 18px;
            border-radius: 25px;
            font-weight: bold;
        }
        .score-excellent { background: linear-gradient(135deg, #10b981, #059669); color: white; }
        .score-good { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
        .score-normal { background: linear-gradient(135deg, #9ca3af, #6b7280); color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>微博热搜产品创意分析报告</h1>
        <p>分析时间：{timestamp}</p>
        <p>热搜总数：{total} | 优秀创意：{excellent} | 良好创意：{good}</p>
    </div>
    <!-- 热点资讯和产品创意列表 -->
</body>
</html>
```

## 报告内容结构

### 1. 报告概览
- 分析时间戳
- 热搜总数统计
- 优秀/良好/普通创意分布
- 评分分布柱状图

### 2. 热点资讯时间线
- 按热度排序的话题列表
- 每个话题的事件脉络和发展时间线
- 热度指数可视化

### 3. 产品创意详情
- 按综合评分降序排列
- **优秀(>80分)**：绿色高亮，★标记，强烈推荐
- **良好(60-80分)**：蓝色标记，◆标记，值得考虑
- **普通(<60分)**：灰色显示，仅供参考

### 4. 评分详情
- 有趣度评分(0-80)
- 有用度评分(0-20)
- 综合评分和评级

## 输出规范

### 文件输出
- 默认路径：`./weibo_product_ideas_YYMMDD.html`（如今天的 `weibo_product_ideas_260115.html`）
- 支持相对路径和绝对路径
- 自定义输出路径示例：`D:\reports\weibo_ideas.html`

### 编码要求
- UTF-8编码
- HTML5标准
- 响应式设计，支持移动端

## 限制与注意事项

1. **API限制**：天行数据API每日有免费调用次数限制（测试key已配置）
2. **搜索限制**：每个话题搜索需控制在合理时间内
3. **创意评估**：评分基于AI分析，实际市场验证需进一步调研
4. **时效性**：热搜分析有时效性，报告需注明分析时间
5. **合规性**：确保内容符合相关法律法规

## 示例使用

### 基础使用
```
分析微博热搜产品创意
```

### 自定义参数
```
分析微博热搜产品创意，前5条，输出到 D:\reports\weibo_ideas.html
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| API请求失败 | 检查API key是否有效，提示用户检查网络 |
| 字段解析错误 | 使用默认值，兼容不同API版本 |
| 搜索无结果 | 跳过该话题，使用默认分析模板 |
| 生成失败 | 输出错误信息和建议解决方案 |
| 评分异常 | 重新评估并记录日志 |

## 评分标准详解

### 有趣度评分（0-80分）

| 评分范围 | 评价 | 说明 |
|----------|------|------|
| 70-80 | 非常有潜力 | 话题新颖、传播性强、用户粘性高 |
| 60-69 | 有潜力 | 话题热度高、有讨论空间 |
| 50-59 | 一般 | 话题中规中矩，缺乏创新 |
| <50 | 较低 | 话题老旧或过于小众 |

### 有用度评分（0-20分）

| 评分范围 | 评价 | 说明 |
|----------|------|------|
| 17-20 | 非常有价值 | 商业模式清晰、市场空间大 |
| 13-16 | 有价值 | 有明确的用户需求 |
| 8-12 | 一般 | 需求存在但变现困难 |
| <8 | 较低 | 市场空间有限 |

## 评级标准

- **优秀 (>80分)**: 绿色高亮，★标记，强烈推荐关注
- **良好 (60-80分)**: 蓝色标记，◆标记，值得考虑
- **普通 (<60分)**: 灰色显示，仅供参考

## 性能要求

1. **响应时间**: 单个话题分析不超过30秒
2. **并发处理**: 最多同时处理5个话题
3. **内存占用**: 单次运行不超过500MB

## 文件结构

```
weibo-trend-product-analyzer/
├── SKILL.md              # 技能定义文档
└── analyzer.py           # Python分析脚本（可选，用于本地运行）
```

## 版本信息

- **版本**: 1.1.0
- **更新日期**: 2026-01-14
- **作者**: Claude Code Skills
- **API**: 天行数据微博热搜API
