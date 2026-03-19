# ecommerce-review-analyzer

Analyze JD/Taobao product links, scrape 5-star reviews, and generate beautiful HTML report with unique selling points.

## Trigger Conditions

Activate this skill when the user's message matches ANY of these patterns:
- `分析京东链接：[URL]` or `分析JD链接：[URL]`
- `分析淘宝链接：[URL]` or `分析TB链接：[URL]`
- Contains keywords like "分析" + ("京东"/"JD"/"淘宝"/"TB") + a valid URL

URL patterns to match:
- `jd.com`, `item.jd.com`
- `taobao.com`, `item.taobao.com`
- `tmall.com`, `detail.tmall.com`

Optional parameter: `抓取N条` (e.g., `抓取50条`) - defaults to 100 if not specified.

**Do NOT trigger for:**
- Questions without URLs (e.g., "京东怎么样")
- Other e-commerce platforms (拼多多, 亚马逊, etc.)

---

## Silent Execution Protocol

**CRITICAL INSTRUCTIONS - READ BEFORE EXECUTING:**

1. **Do NOT ask for confirmation to proceed.** Execute the full workflow automatically.
2. **Generate the complete HTML report in one response.** No mid-process status updates asking "should I continue?"
3. **If data is missing, use defaults.** Do not ask the user for clarification.
4. **Handle errors silently.** Log issues in the report if needed, but never stop to ask "what should I do?"
5. **Allow automatic generation of full report** even if content is long (100 reviews). NO chunking confirmation needed.
6. **The ONLY exceptions that require user interaction:**
   - When login is required and not yet completed
   - When 5-star reviews are less than 20 (stop and inform user)

---

## Input Parsing

Extract from user message:
```
URL: Required - the product link
COUNT: Optional - number of reviews to scrape (default: 100)
```

**Parsing Rules:**
- If user writes `抓取50条` or `50条评论`, set COUNT = 50
- If no count specified, COUNT = 100
- Detect platform from URL domain automatically
- Treat tmall.com as Taobao system
- **IMPORTANT: Only scrape 5-STAR reviews (not all positive reviews)**

---

## Workflow Steps

### Step 1: Initialize Browser
```
Use `browser navigate [URL]` to open the product page.
```

### Step 2: Login Detection
```
After page loads, check login status:

LOGGED IN SIGNALS (if ANY present, user is logged in):
- Page shows "我的订单" link/button
- Page displays username/nickname in header
- User avatar is visible in navigation
- "退出" or "注销" button visible

NOT LOGGED IN SIGNALS:
- Page contains text: "请登录" / "登录后查看" / "请先登录"
- Login modal/popup appears
- Review section shows login prompt instead of reviews
- URL redirects to login.taobao.com or passport.jd.com

IF NOT logged in:
  → Output EXACTLY: "检测到需要登录才能查看评论，请在浏览器中完成登录后回复「已登录」或「OK」"
  → STOP and wait for user response
  → When user replies "已登录" / "OK" / "好了" / "done", continue to Step 3

IF already logged in:
  → Proceed silently to Step 3 (do NOT mention login status)
```

### Step 3: Extract Product Info
```
Scrape from the page:
- Product name (商品名称)
- Price (价格)
- Store name (店铺名称)
- Overall rating (评分)
- Total review count (评论总数)
- Rating distribution if available (好评/中评/差评数量)

If any field is unavailable, use "未获取到" as placeholder. Do NOT ask user.
```

### Step 4: Navigate to Reviews
```
JD: Click "商品评价" tab, then filter by "5星" or "好评"
Taobao/Tmall: Click "累计评论" or "评价" tab, filter by 5-star reviews

Use `browser act` commands to:
1. Click the reviews tab
2. Select "5星" filter (IMPORTANT: must be 5-star only, not general positive)
3. Wait for reviews to load
```

### Step 5: Check Review Count
```
After filtering 5-star reviews, check the total count:

IF 5-star review count < 20:
  → Output: "该商品5星评论仅有 [N] 条，样本量过少（需至少20条），无法生成有效分析报告。建议选择评论更多的商品进行分析。"
  → Close browser and STOP

IF 5-star review count >= 20:
  → Continue to Step 6
```

### Step 6: Scrape Reviews
```
Collect up to [COUNT] 5-star reviews (default 100):

LOOP:
  - Extract visible review texts
  - Scroll down to load more
  - Stop when reaching COUNT or no more reviews

SKIP these reviews (silently, no warning):
  - Image-only reviews with no text
  - Reviews with only "好评" or single characters
  - Duplicate reviews

COLLECT for each review:
  - Review text content
  - Review date
  - User purchased SKU (if visible)
  - Any tags/labels (e.g., "质量好", "物流快")
```

### Step 7: Analyze Reviews
```
Process collected reviews using NLP analysis:

1. KEYWORD EXTRACTION
   - Identify frequently mentioned positive attributes
   - Group similar terms (e.g., "质量好"/"质量不错"/"品质好")
   - Calculate frequency for each keyword

2. ADVANTAGE CLUSTERING
   - Cluster reviews by theme (质量/物流/包装/性价比/外观/服务/etc.)
   - Count frequency of each advantage
   - Rank by frequency descending

3. SENTIMENT HIGHLIGHTS
   - Extract most enthusiastic/detailed reviews as "user voice"
   - Pick 2-3 representative quotes per advantage category

4. RATING DISTRIBUTION
   - Calculate percentage breakdown if data available
```

### Step 8: Generate HTML Report
```
Create a beautiful, professional HTML report with the following sections:

REPORT STRUCTURE:
1. Header - Product name, store, date
2. Product Info Card - Image, price, rating, sales
3. Rating Distribution Chart - Visual bar/pie chart
4. Core Advantages - Ranked list with frequency badges
5. User Voice Gallery - Selected review quotes in cards
6. Keyword Cloud - Visual keyword frequency display
7. Purchase Recommendation - AI-generated summary

DESIGN REQUIREMENTS:
- Modern, clean aesthetic (not generic)
- Responsive layout
- Color scheme: Professional blues/grays with accent colors
- Typography: Clear hierarchy, readable fonts
- Charts: Use CSS/SVG for visualizations (no external dependencies)
- Mobile-friendly

FILE SAVING:
- Create directory: ./report/ (if not exists)
- Filename format: [商品名称简写]_[YYYYMMDD].html
- Example: 路由器收纳盒_20260309.html
- Sanitize filename (remove special characters)
```

### Step 9: Display Report
```
After saving the HTML file:
1. Use `browser navigate file:///path/to/report.html` to open the report
2. Take a screenshot to show user
3. Output the file path for user reference
```

### Step 10: Cleanup
```
Output summary:
- Report saved location
- Number of reviews analyzed
- Key findings summary (2-3 sentences)

Keep browser open showing the report (do not close).
```

---

## Error Handling (Silent)

| Error | Auto-Response |
|-------|---------------|
| Invalid URL / 404 | Output: `无法访问该商品页面，请检查链接是否正确。` Then STOP. |
| Product removed/下架 | Output: `该商品已下架或不存在。` Then STOP. |
| 5-star reviews < 20 | Output: `该商品5星评论仅有N条，样本量过少，无法生成有效分析。` Then STOP. |
| Network timeout | Retry once. If still fails, output collected data and generate partial report. |
| Page structure changed | Try alternative selectors. If fails, report with available data. |
| Blocked by anti-bot | Output: `页面访问受限，请稍后重试或尝试手动登录后再试。` Then STOP. |
| Cannot create report directory | Use current directory as fallback. |
| Filename conflict | Append timestamp suffix (e.g., _1, _2). |

**NEVER ask "what should I do?" - always execute the defined fallback.**

---

## HTML Report Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[商品名称] - 5星评论分析报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .report-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header .meta {
            opacity: 0.8;
            font-size: 14px;
        }
        .section {
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }
        .section:last-child { border-bottom: none; }
        .section-title {
            font-size: 20px;
            color: #1a1a2e;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section-title::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }
        .product-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .info-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
        }
        .info-item label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .info-item value {
            display: block;
            font-size: 18px;
            font-weight: 600;
            color: #1a1a2e;
            margin-top: 5px;
        }
        .advantage-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .advantage-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 20px;
            background: #f8f9fa;
            border-radius: 12px;
            transition: transform 0.2s;
        }
        .advantage-item:hover {
            transform: translateX(5px);
        }
        .advantage-rank {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .advantage-content {
            flex: 1;
        }
        .advantage-name {
            font-weight: 600;
            color: #1a1a2e;
        }
        .advantage-bar {
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        .advantage-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
        }
        .advantage-count {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .review-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        .review-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        .review-text {
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 10px;
        }
        .review-meta {
            font-size: 12px;
            color: #999;
        }
        .keyword-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .keyword-tag {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        .recommendation {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
        }
        .recommendation h3 {
            margin-bottom: 15px;
        }
        .recommendation p {
            opacity: 0.95;
            line-height: 1.8;
        }
        .rating-chart {
            display: flex;
            align-items: end;
            gap: 10px;
            height: 120px;
            padding: 20px 0;
        }
        .rating-bar {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .rating-bar-fill {
            width: 100%;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px 8px 0 0;
            min-height: 10px;
        }
        .rating-label {
            font-size: 12px;
            color: #666;
        }
        .rating-value {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a2e;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="report-card">
            <!-- Header -->
            <div class="header">
                <h1>[商品名称]</h1>
                <div class="meta">[店铺名称] | 分析日期: [YYYY-MM-DD] | 样本: [N]条5星评论</div>
            </div>

            <!-- Product Info -->
            <div class="section">
                <h2 class="section-title">商品信息</h2>
                <div class="product-info">
                    <div class="info-item">
                        <label>价格</label>
                        <value>[价格]</value>
                    </div>
                    <div class="info-item">
                        <label>店铺评分</label>
                        <value>[评分]</value>
                    </div>
                    <div class="info-item">
                        <label>销量</label>
                        <value>[销量]</value>
                    </div>
                    <div class="info-item">
                        <label>5星评论数</label>
                        <value>[5星数量]</value>
                    </div>
                </div>
            </div>

            <!-- Rating Distribution -->
            <div class="section">
                <h2 class="section-title">评分分布</h2>
                <div class="rating-chart">
                    <!-- Dynamic bars based on data -->
                </div>
            </div>

            <!-- Core Advantages -->
            <div class="section">
                <h2 class="section-title">核心优点</h2>
                <div class="advantage-list">
                    <!-- Dynamic advantage items -->
                </div>
            </div>

            <!-- User Voice -->
            <div class="section">
                <h2 class="section-title">用户原声精选</h2>
                <div class="review-grid">
                    <!-- Dynamic review cards -->
                </div>
            </div>

            <!-- Keyword Cloud -->
            <div class="section">
                <h2 class="section-title">高频关键词</h2>
                <div class="keyword-cloud">
                    <!-- Dynamic keyword tags -->
                </div>
            </div>

            <!-- Recommendation -->
            <div class="section">
                <h2 class="section-title">购买建议</h2>
                <div class="recommendation">
                    <h3>AI 分析结论</h3>
                    <p>[基于评论数据的综合购买建议]</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

---

## Examples

### Good Example (Correct Behavior)

**User:** 分析淘宝链接：https://detail.tmall.com/item.htm?id=123456

**Assistant:**
[Immediately starts browser, navigates, checks login, scrapes 5-star reviews, analyzes, generates HTML]

报告已生成并保存至: `./report/小米电视55寸_20260309.html`

已在浏览器中打开报告预览。

**分析摘要：**
- 共分析 87 条5星评论
- 核心优点：画质清晰(52次)、性价比高(41次)、物流快速(38次)
- 推荐指数：强烈推荐

---

### Anti-Pattern (FORBIDDEN Behavior)

**User:** 分析京东链接：https://item.jd.com/100012345.html

**WRONG - Do NOT do this:**
```
我已经收集了50条评论。

要继续收集更多吗？还是现在就生成报告？  ← FORBIDDEN!
```

**CORRECT:**
```
[自动收集完100条或全部可用评论，一次性生成完整HTML报告]
```

---

### Anti-Pattern 2 (Review Count Check)

**WRONG:**
```
这个商品只有15条5星评论，要继续分析吗？  ← FORBIDDEN!
```

**CORRECT:**
```
该商品5星评论仅有 15 条，样本量过少（需至少20条），无法生成有效分析报告。建议选择评论更多的商品进行分析。
```

---

## Platform-Specific Notes

### JD (京东)
- Reviews tab: "商品评价"
- 5-star filter: Look for "5星" or star rating filter
- Reviews are usually paginated, scroll or click "下一页"
- Login indicator: Top right shows username or "我的订单"

### Taobao (淘宝) / Tmall (天猫)
- Reviews section: "累计评论" or "评价"
- Filter by rating stars if available
- May need to scroll to load more reviews
- Some reviews require clicking "展开" to see full text
- Login indicator: Top shows username, "我的淘宝", "我的订单"

---

## Output Files

**Directory Structure:**
```
./report/
├── [商品名称]_[YYYYMMDD].html
├── [商品名称]_[YYYYMMDD].html
└── ...
```

**Filename Rules:**
- Use simplified product name (first 10-15 Chinese characters)
- Remove special characters: / \ : * ? " < > |
- Replace spaces with underscores
- Date format: YYYYMMDD
- If filename exists, append _1, _2, etc.
