---
name: paper-interpreter
description: arXiv 论文解读助手 - 自动解析论文、生成黄叔风格文章、输出 HTML/PDF
license: MIT
version: 1.0.0
---

# 📄 Paper Interpreter (论文解读助手)

## 静默执行协议 (Quiet Mode Protocol)

> **IMPORTANT**: Read and obey these instructions before proceeding.

### Execution Rules
1. **DO NOT** ask for confirmation to proceed during stages - use the defined confirmation format at each stage end
2. **DO NOT** request additional information - if data is missing, use defined defaults
3. **Generate outputs in full** - complete each stage before moving to the next
4. **If API fails**, retry 3 times with exponential backoff before using fallback
5. **If stage fails**, log the error and continue with default values

### Confirmation Format
After completing each stage, output the confirmation block exactly as specified:
```
---
**Stage X: [Stage Name] Completed**

[Summary of what was done]

❓ **[Confirm?]**: [Confirmation question for user]
---
```

### Default Values
- `title_zh`: "未知论文"
- `authors`: [{"name": "Unknown Author"}]
- `images`: Generate 3 placeholder colored rectangles if API fails
- `language`: Use Chinese for all outputs

---

## 触发格式

```
/paper <input>
/论文 <input>
```

**Inputs:**
- arXiv URL: `/paper https://arxiv.org/abs/2501.12345`
- Local PDF path: `/paper /path/to/paper.pdf`
- Paper description: `/论文 我想了解关于 Transformer 的论文`

---

## 工作流程 (6 Stages)

### Stage 1: 论文解析 (Paper Parsing)

**Input:** arXiv URL / PDF path / Paper description

**Tasks:**
1. Extract paper identifier from input
2. Fetch metadata from arXiv API:
   - Title (EN/ZH)
   - Abstract
   - Authors and institutions
   - Categories
   - Published date
3. Download PDF (if URL provided) or read local PDF
4. Extract main content sections

**Output:**
```json
{
  "paper_id": "2501.12345",
  "title_en": "Chain-of-Thought Prompting...",
  "title_zh": "思维链提示...",
  "abstract": "...",
  "authors": [{"name": "...", "institution": "..."}],
  "categories": ["cs.CL", "cs.LG"],
  "published_date": "2022-01-28"
}
```

**Confirmation:**
```
---
**Stage 1: 论文解析 Completed**

- Paper ID: 2501.12345
- Title: 思维链提示在大语言模型中引出推理能力
- Authors: Jason Wei (Google Research), Xuezhi Wang (Google Research)

❓ **Confirm?**: 论文信息是否正确？ (回复 Y 继续 / N 重新输入)
---
```

---

### Stage 2: 黄叔风格文章生成

**Target:** ~3000 Chinese characters

**Structure:**
| Section | Target | Requirements |
|---------|--------|--------------|
| 引子 (Lead-in) | ~200 chars | Hook reader, set context |
| 核心发现 (Core Findings) | ~800 chars | Main contribution, key metrics, **z1 analogy ≥400 chars** |
| 技术细节 (Technical Details) | ~1000 chars | Three-layer progressive, **second person ≥30%** |
| 现实意义 (Real-world Impact) | ~600 chars | Applications, implications |
| 总结 (Summary) | ~400 chars | Key takeaways, memorable closing |

**z1类比要求:**
- Use ONE vivid everyday analogy
- Minimum 400 characters
- Make technical concept accessible

**第二人称要求:**
- Use "你", "你的" frequently in technical section
- Target: ≥30% of technical section

**三层递进解释:**
- L1: Intuitive (说人话) - Everyday analogy
- L2: Technical (怎么做到的) - Mechanism
- L3: Mathematical (公式化) - Formal foundation

**Output Format:**
```markdown
## 引子

[200 chars engaging hook]

## 核心发现

[Main findings with z1 analogy]

### z1类比：让AI学会"思考"
[400+ chars vivid analogy]

## 技术细节

### L1: 直观理解（说人话）
[Concept in simple terms]

### L2: 技术原理（怎么做到的）
[Technical mechanism]

### L3: 数学基础（公式化表达）
[Mathematical/formal explanation]

## 现实意义

[600 chars on applications and impact]

## 总结

[400 chars closing]
```

**Confirmation:**
```
---
**Stage 2: 黄叔风格文章生成 Completed**

- Word count: 3,247 characters
- z1 analogy: ✓ (485 chars)
- Second person: ✓ (32%)
- Three layers: ✓ Complete

❓ **Confirm?**: 文章风格和内容是否满意？ (回复 Y 继续 / 修改内容...)
---
```

---

### Stage 3: 配图生成 (Image Generation)

**API:** yunwu.ai - Geini 2.0 Flash

**API Key:** sk-3hmgQ0Y5xyReFQO7AnR9pP4ZW8DoBgvGJXMX0WtZu9PIlw48

**Tasks:**
1. Generate 5 images based on paper sections
2. Style: 暖调现代风 (Warm modern style)
3. Save to: `./images/{paper_id}_{1-5}.png`

**Image Prompts:**

| Image | Section | Prompt Style |
|-------|---------|--------------|
| 1 | 引子 | 引人入胜的视觉隐喻 |
| 2 | 核心发现 | 核心概念可视化 |
| 3 | 技术细节 | 技术架构图解 |
| 4 | 现实意义 | 应用场景展示 |
| 5 | 总结 | 总结性抽象艺术 |

**API Call:**
```
ENDPOINT: https://yunwu.ai/api/generate
MODEL: geini-2.0-flash
STYLE: 暖调现代风 (warm colors, modern aesthetic)
SIZE: 1024x1024
```

**Fallback (if API fails):**
- Generate SVG placeholders with section titles
- Continue without interruption

**Confirmation:**
```
---
**Stage 3: 配图生成 Completed**

- Generated: 5 images
- Style: 暖调现代风
- Saved to: images/2501.12345_1.png ~ 5.png

❓ **Confirm?**: 配图质量是否接受？ (回复 Y 继续 / R 重新生成)
---
```

---

### Stage 4: HTML 生成

**Template:** `template.html`

**Style:** 暖调现代风 (Warm Modern Style)

**Color Palette:**
```css
--primary: #FF6B35;      /* 暖橙 */
--secondary: #F7C59F;    /* 暖杏 */
--background: #FFFAF6;   /* 暖白 */
--text: #2D3047;         /* 深蓝灰 */
--accent: #EFEFD0;       /* 暖黄 */
```

**Features:**
- Scroll-triggered animations (fade-in, slide-up)
- Progress bar
- Responsive design (mobile-first)
- Card-based layout
- Smooth transitions

**Output:** `./output/{title_zh}/index.html`

**Confirmation:**
```
---
**Stage 4: HTML 生成 Completed**

- File: output/思维链提示/index.html
- Style: 暖调现代风 + 滚动动画
- Responsive: ✓ Mobile/Desktop

❓ **Confirm?**: 排版和动画效果是否满意？ (回复 Y 继续)
---
```

---

### Stage 5: PDF 生成

**Engines (in order):**
1. Playwright
2. WeasyPrint
3. pdfkit

**Content:** 完整版 (封面 + 目录 + 正文 + 引用)

**Font:** NotoSansSC (auto-download if missing)

**Output:** `./output/{title_zh}/{title_zh}.pdf`

**Confirmation:**
```
---
**Stage 5: PDF 生成 Completed**

- File: output/思维链提示/思维链提示.pdf
- Size: 2.3 MB
- Pages: 12
- Content: 封面 + 目录 + 正文 + 引用

❓ **Confirm?**: PDF 文件是否正确？ (回复 Y 继续)
---
```

---

### Stage 6: 文件输出

**Tasks:**
1. Create output directory: `./output/{title_zh}/`
2. Move/copy files:
   - `index.html`
   - `{title_zh}.pdf`
   - `{title_zh}.md` (original markdown)
   - `{title_zh}_log.txt` (execution log)
   - `./images/*` → `./output/{title_zh}/images/`
3. Clean up temporary files

**Final Structure:**
```
output/{title_zh}/
├── index.html              # 网页版
├── {title_zh}.pdf          # PDF完整版
├── {title_zh}.md           # Markdown原文
├── {title_zh}_log.txt      # 执行日志
└── images/
    ├── 1.png
    ├── 2.png
    ├── 3.png
    ├── 4.png
    └── 5.png
```

**Completion Output:**
```
========================================
✅ 论文解读完成！
========================================

📁 输出目录: output/思维链提示/

📄 文件列表:
├── index.html          (网页版)
├── 思维链提示.pdf      (PDF版)
├── 思维链提示.md       (Markdown原文)
├── 思维链提示_log.txt  (执行日志)
└── images/
    └── 1.png ~ 5.png   (配图)

🎯 使用方法:
- 浏览器打开 index.html 查看网页版
- 打开 PDF 查看/打印完整版
```

---

## 容错机制 (Error Handling)

| Error | Retry | Fallback |
|-------|-------|----------|
| arXiv API timeout | 3x (2s delay) | Use default metadata |
| PDF download fails | 2x (5s delay) | Skip, continue without PDF |
| yunwu.ai API fails | 3x (exponential) | Generate placeholder SVGs |
| PDF generation fails | 2x (10s delay) | Output HTML only |
| Missing template.html | N/A | FAIL - critical |
| Missing font | N/A | Auto-download NotoSansSC |
| Invalid input format | 1x | Ask for clarification once |

---

## 决策树 (Decision Tree)

```
                          /paper <input>
                              │
                    ┌─────────▼─────────┐
                    │ Parse input       │
                    │ - arXiv URL       │
                    │ - Local PDF       │
                    │ - Description     │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
      ┌───────▼───────┐               ┌───────▼───────┐
      │ arXiv API    │               │ Local PDF    │
      │ succeeds     │               │ file exists  │
      └───────┬───────┘               └───────┬───────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Generate Article  │
                    │ (Stage 2)         │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Generate Images   │
                    │ (Stage 3)         │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
      ┌───────▼───────┐               ┌───────▼───────┐
      │ yunwu.ai     │               │ API fails     │
      │ succeeds     │               │               │
      └───────┬───────┘               └───────┬───────┘
              │                               │
              │                        ┌───────▼───────┐
              │                        │ Placeholder   │
              │                        │ SVGs          │
              │                        └───────┬───────┘
              └───────────────┬───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Generate HTML     │
                    │ (Stage 4)         │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Generate PDF      │
                    │ (Stage 5)         │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
      ┌───────▼───────┐               ┌───────▼───────┐
      │ PDF gen      │               │ PDF gen      │
      │ succeeds     │               │ fails        │
      └───────┬───────┘               └───────┬───────┘
              │                               │
              │                        ┌───────▼───────┐
              │                        │ Output HTML   │
              │                        │ only          │
              │                        └───────────────┘
              └───────────────┬───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Organize Files    │
                    │ (Stage 6)         │
                    └─────────┬─────────┘
                              │
                         ┌────▼────┐
                         │ COMPLETE│
                         └─────────┘
```

---

## Few-Shot Examples

### ✅ Good Case (Standard Execution)

**User Input:**
```
/paper https://arxiv.org/abs/2310.12345
```

**Expected Flow:**
```
[Stage 1] Parsed paper ID: 2310.12345
[Stage 1] Fetched metadata: 标题: XXX, 作者: 3人
---
**Stage 1: 论文解析 Completed**
- Paper ID: 2310.12345
- Title: ...
❓ **Confirm?**: 论文信息是否正确？ (回复 Y 继续 / N 重新输入)
---

Y
[Stage 2] Generated article: 3,247 chars
---
**Stage 2: 黄叔风格文章生成 Completed**
- Word count: 3,247
- z1 analogy: ✓
❓ **Confirm?**: 文章风格和内容是否满意？
---

Y
[Stage 3] Generated 5 images
---
**Stage 3: 配图生成 Completed**
- Generated: 5 images
❓ **Confirm?**: 配图质量是否接受？
---

Y
[Stage 4] Generated HTML
[Stage 5] Generated PDF (2.3MB)
[Stage 6] Organized files
========================================
✅ 论文解读完成！
========================================
```

### ❌ Anti-Patterns (Forbidden)

**❌ BAD: Mid-stage confirmation**
```
[Stage 2] I generated the first paragraph. Should I continue?
[Stage 2] Do you want me to add more technical details?
```

**WHY:** Breaks atomicity. Generate full output, then confirm once.

**❌ BAD: Requesting more info**
```
[Stage 1] I couldn't find this paper. What arXiv ID should I use?
[Stage 2] What style do you prefer for the analogies?
```

**WHY:** Use defined defaults, ask for clarification only once at start.

**❌ BAD: Mid-workflow warnings**
```
[Stage 3] Warning: Image generation is taking longer than expected.
[Stage 3] Should I continue waiting or use placeholders?
```

**WHY:** Handle errors silently with fallbacks. Confirm after completion.

**❌ BAD: Open-ended questions**
```
[Stage 2] Is the technical depth appropriate? Would you like adjustments?
[Stage 4] Are the colors what you expected?
```

**WHY:** Ask specific Yes/No questions, not open-ended feedback.

---

## 文件依赖

| File | Required | Description |
|------|----------|-------------|
| `template.html` | ✅ Yes | HTML template with warm modern styling |
| `generate_pdf.py` | ✅ Yes | PDF generation script |
| `yunwu_api_key` | ✅ Yes | Set in environment variable `YUNWU_API_KEY` |

## 环境依赖

```bash
# Python packages
pip install requests beautifulsoup4 pdfplumber

# Optional (for PDF generation, one of)
pip install playwright && playwright install chromium
pip install weasyprint
pip install pdfkit && apt-get install wkhtmltopdf
```

---

## 快速参考

| Command | Action |
|---------|--------|
| `/paper <url>` | 解析 arXiv 论文 |
| `/论文 <path>` | 解析本地 PDF |
| `Y` | 确认继续 |
| `N` | 重新输入 / 取消 |
| `R` | 重新生成当前阶段 |
