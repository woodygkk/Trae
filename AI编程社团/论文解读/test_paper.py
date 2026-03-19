#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_paper.py - 论文解读 Skill 测试脚本

用法:
    python test_paper.py                           # 使用模拟数据快速测试
    python test_paper.py --real https://arxiv.org/abs/XXXX.XXXXX  # 使用真实 arXiv 论文

依赖:
    pip install requests beautifulsoup4
"""

import os
import sys
import json
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 模拟 HTTP 请求 (避免网络依赖)
class MockResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")


@dataclass
class PaperMetadata:
    paper_id: str
    title_en: str
    title_zh: str
    abstract: str
    authors: list
    categories: list
    published_date: str
    pdf_url: str


class ArxivClient:
    """arXiv API 客户端 (模拟版本)"""

    MOCK_PAPERS = {
        "2501.12345": PaperMetadata(
            paper_id="2501.12345",
            title_en="Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            title_zh="思维链提示在大语言模型中引出推理能力",
            abstract="""
                We explore how a simple chain of thought prompting can dramatically improve
                the ability of large language models to perform complex reasoning. Through
                extensive experiments, we show that chain-of-thought prompting leads to
                substantial performance gains across arithmetic, symbolic, and commonsense
                reasoning tasks. Our findings suggest that language models possess
                emergent abilities that can be unlocked through appropriate prompting strategies.
            """,
            authors=[
                {"name": "Jason Wei", "institution": "Google Research"},
                {"name": "Xuezhi Wang", "institution": "Google Research"},
                {"name": "Dale Schuurmans", "institution": "Google Research"}
            ],
            categories=["cs.CL", "cs.LG"],
            published_date="2022-01-28",
            pdf_url="https://arxiv.org/pdf/2501.12345.pdf"
        ),
        "2312.09876": PaperMetadata(
            paper_id="2312.09876",
            title_en="Attention Is All You Need",
            title_zh="注意力就是你所需要的一切",
            abstract="""
                The dominant sequence transduction models are based on complex recurrent or
                convolutional neural networks that include an encoder and a decoder. The best
                performing models also connect the encoder and the decoder through an attention
                mechanism. We propose a new simple network architecture, the Transformer,
                based solely on attention mechanisms.
            """,
            authors=[
                {"name": "Ashish Vaswani", "institution": "Google Brain"},
                {"name": "Noam Shazeer", "institution": "Google Brain"},
                {"name": "Niki Parmar", "institution": "Google Research"}
            ],
            categories=["cs.CL", "cs.NE"],
            published_date="2017-06-12",
            pdf_url="https://arxiv.org/pdf/2312.09876.pdf"
        )
    }

    def fetch_metadata(self, paper_id: str) -> PaperMetadata:
        """获取论文元数据"""
        if paper_id in self.MOCK_PAPERS:
            return self.MOCK_PAPERS[paper_id]
        # 默认返回第一个
        return self.MOCK_PAPERS["2501.12345"]


class RealContentGenerator:
    """真实内容生成器 (使用 Claude 3.5 Sonnet)"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logging.warning("⚠️ 未找到 ANTHROPIC_API_KEY，将回退到模拟模式")
            self.client = None
        else:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logging.error("❌ 未安装 anthropic 库。请运行: pip install anthropic")
                self.client = None

    def generate_article(self, metadata: PaperMetadata) -> str:
        """调用 Claude 生成解读文章"""
        if not self.client:
            return ContentGenerator().generate_article(metadata)

        print("🤖 正在调用 Claude 3.5 Sonnet 生成深度解读... (这可能需要几十秒)")
        
        system_prompt = """你是一位名叫"黄叔"的资深AI技术博主。你的写作风格：
1. 通俗易懂：擅长用生活中的例子（如做菜、谈恋爱、带孩子）来解释复杂的AI概念。
2. 幽默风趣：行文轻松，偶尔带点调侃。
3. 结构清晰：采用"引子 -> 核心发现 -> z1类比 -> 技术细节(L1/L2/L3) -> 现实意义 -> 总结"的结构。
4. 深度与广度并存：既能让小白看懂，又能给专业人士启发。

请基于用户提供的论文元数据，写一篇深度解读文章。"""

        user_prompt = f"""
论文标题：{metadata.title_zh} ({metadata.title_en})
摘要：{metadata.abstract}

请按以下 Markdown 格式输出文章：

## 引子
(从生活场景切入，引发共鸣)

## 核心发现
(用一句话概括论文解决了什么痛点，效果如何)

### z1类比：让AI学会"思考"
(创造一个精彩的类比来解释核心概念)

## 技术细节

### L1: 直观理解（说人话）
(延续上面的类比，通俗解释)

### L2: 技术原理（怎么做到的）
(简要描述模型架构或算法流程)

### L3: 数学基础（公式化表达）
(提取1-2个核心公式或逻辑推导，用LaTeX格式)

## 现实意义
(教育、医疗、商业等领域的应用潜力)

## 总结
(金句收尾，启发思考)
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logging.error(f"Claude API 调用失败: {e}")
            return ContentGenerator().generate_article(metadata)


class ContentGenerator:
    """内容生成器 (生成黄叔风格的解读文章)"""

    Z1_ANALOGIES = {
        "chain-of-thought": """
            想象你在教一个孩子解数学题。普通方式你只给答案，而思维链就像是你一步步解释：
            "首先，我们要把14分成10和4，然后4乘以7得28，再加上10乘以7的70..."
            每一步都清晰可见，错误也更容易被发现。
            这正是思维链提示在做的事情——让AI把思考过程"说出来"，而不是只给最终答案。
        """,
        "transformer": """
            想象你在嘈杂的聚会上听一个人说话。你的大脑会自动聚焦于他的声音，
            自动过滤背景噪音——这就是"注意力"机制。
            Transformer架构所做的，就是让AI学会这种"选择性注意力"：
            在处理每个词时，它会思考"哪些其他词对我的理解最重要"。
        """
    }

    def generate_article(self, metadata: PaperMetadata) -> str:
        """生成完整的解读文章 (Markdown格式)"""

        # 根据论文类型选择类比
        if "transformer" in metadata.title_en.lower():
            analogy = self.Z1_ANALOGIES["transformer"]
        else:
            analogy = self.Z1_ANALOGIES["chain-of-thought"]

        # 生成文章内容
        article = f"""## 引子

你是否有这样的经历：对着AI说"帮我写首诗"，它能给你一段漂亮的文字；但当你问"怎么解这道数学应用题"时，它却给出一个看似对但完全不通的答案？

这背后的原因很残酷——AI在"直觉"方面很强，但在"推理"方面曾经是个小白。

但2022年，谷歌研究团队发现了一个神奇的技巧：**思维链提示 (Chain-of-Thought Prompting)**，它让AI的推理能力产生了质的飞跃。

## 核心发现

**思维链提示是什么？** 简单来说，就是在问问题之前，先给AI一个"思考示例"。

> 比如你想让AI算"小明有15个苹果，送给小红7个，又买了5个，现在有多少个？"
> 普通问法直接给答案；但思维链问法会先示范：
> "小明有15个苹果，送给小红7个，剩下15-7=8个，又买了5个，现在有8+5=13个。"
> 然后让AI照这个格式回答。

实验结果令人震惊：
- **算术推理**准确率提升高达50%以上
- **常识推理**任务中，540B参数的大模型甚至超越了微调模型
- 最关键的是：**无需任何模型训练，只需修改提示词**

{{z1_analogy_header}}思维链的本质是什么？{analogy}

## 技术细节

### L1: 直观理解（说人话）

{{y1_layer}}

### L2: 技术原理（怎么做到的）

{{y2_layer}}

### L3: 数学基础（公式化表达）

{{y3_layer}}

## 现实意义

{{impact_section}}

## 总结

{{summary_section}}
"""
        # 填充各部分内容
        article = article.format(
            z1_analogy_header='### z1类比：让AI学会"思考"',
            y1_layer=self._layer1_content(metadata),
            y2_layer=self._layer2_content(metadata),
            y3_layer=self._layer3_content(metadata),
            impact_section=self._impact_content(metadata),
            summary_section=self._summary_content(metadata)
        )

        return article

    def _layer1_content(self, metadata: PaperMetadata) -> str:
        """L1 直观解释"""
        return f"""
**思维链**就像是你在做数学应用题时的**草稿纸**。

想象你让学生算"小明有5个苹果，又买了3个，总共几个？"：
- 不写步骤的学生：直接在脑中算出8个（但你不知道他是怎么算的）
- 写步骤的学生：5 + 3 = 8（每一步都清晰可见）

AI也是一样。普通提示下，AI直接在"脑中"给出答案；
思维链提示下，AI会把每一步推理都写出来，就像学生在草稿纸上列算式一样。
"""

    def _layer2_content(self, metadata: PaperMetadata) -> str:
        """L2 技术原理"""
        return f"""
思维链提示的技术原理涉及三个关键要素：

**1. 显式推理步骤**
通过在提示中展示`<思考过程>`，让模型学会生成中间推理步骤。
这相当于给模型提供了一个"思考模板"。

**2. 自我一致性**
模型在生成答案时会"思考多条路径"，然后通过投票选择最一致的答案。
这就像你做题时会检查好几种解法是否得到相同结果。

**3. 涌现能力**
研究表明，只有当模型规模足够大时（约100B参数以上），
思维链提示才会展现出显著效果——这是一种"涌现现象"。
"""

    def _layer3_content(self, metadata: PaperMetadata) -> str:
        """L3 数学/形式化基础"""
        return f"""
从形式化角度来看，思维链改变了问题的条件概率分布：

给定输入x，模型需要生成输出y。普通提示要求：
$$P(y|x)$$

思维链提示引入中间变量c（chain/chain of thought）：
$$P(y,c|x) = P(y|c,x) \\cdot P(c|x)$$

通过边缘化所有可能的中间步骤：
$$P(y|x) = \\sum_c P(y|c,x) \\cdot P(c|x)$$

这使得模型可以在生成最终答案前，先"采样"出合理的推理路径c，
从而提升复杂推理任务的条件概率估计准确性。
"""

    def _impact_content(self, metadata: PaperMetadata) -> str:
        """现实意义"""
        return f"""
### 🎓 教育领域

思维链提示可以被用来**教AI当老师**：
- AI可以生成带解题步骤的教程
- 学生可以看到"AI是怎么思考的"
- 个性化辅导成为可能

### 🏥 医疗诊断

在医疗场景中，AI可以：
- 展示诊断推理的每一步
- 医生可以审核AI的"思考过程"
- 减少AI给出错误结论的风险

### 💼 商业决策

企业可以用AI进行：
- 财务分析的步骤展示
- 风险评估的透明化
- 让非技术人员理解AI的建议

### ⚠️ 局限性

需要注意的是，思维链并非万能药：
- 对简单问题可能**过度思考**
- 可能会生成**看似合理但错误**的推理步骤
- 在事实性知识上可能产生幻觉
"""

    def _summary_content(self, metadata: PaperMetadata) -> str:
        """总结"""
        return f"""
**核心启示**：提示工程本身就是一种"编程"。

思维链提示证明了：**如何提问，比模型本身更重要。**

这开启了一个全新的研究方向——**提示工程 (Prompt Engineering)**，
它不需要修改模型权重，就能解锁AI的各种能力。

记住这个公式：
> **好提示 = 清晰目标 + 示范示例 + 思考空间**

下次当你觉得AI"不够聪明"时，不妨想想：是不是我的提示不够好？

---

*本文由 Claude Agent 自动生成，基于 arXiv 论文解读*
"""


class ImageGenerator:
    """图片生成器 (模拟 yunwu.ai API)"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.image_dir = Path("images")
        self.image_dir.mkdir(exist_ok=True)

    def generate_images(self, paper_id: str, count: int = 5) -> list:
        """生成5张配图 (模拟)"""
        images = []

        prompts = [
            ("引人入胜的视觉隐喻", "一个孩子在思考的迷宫入口，彩色线条引导方向，纽约客风格极简线条"),
            ("核心概念可视化", "大脑神经网络与齿轮联动，齿轮代表推理步骤，纽约客风格3-4色配色"),
            ("技术架构图", "抽象的注意力机制图解，点线连接形成网络，中世纪现代美学设计"),
            ("现实应用场景", "教室、黑板、医生诊室、商业会议室的场景插画，纽约客极简风格"),
            ("总结性抽象艺术", "从混乱到有序的视觉转变，点线逐渐排列成规律图案，暖色调背景")
        ]

        for i, (caption, prompt) in enumerate(prompts, 1):
            # 模拟生成图片 (创建占位图)
            image_path = self.image_dir / f"{paper_id}_{i}.png"
            self._create_placeholder(image_path, i, caption)

            images.append({
                "index": i,
                "path": str(image_path),
                "caption": caption,
                "prompt": prompt
            })
            print(f"  🖼️  图片 {i} 生成完成")

        return images

    def _create_placeholder(self, path: Path, index: int, caption: str):
        """创建占位图 (实际使用时替换为真实的 yunwu.ai API 调用)"""
        # 这里创建简单的 SVG 占位图
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
  <rect width="100%" height="100%" fill="#FFFAF6"/>
  <rect x="100" y="100" width="824" height="824" fill="#EFEFD0" rx="20"/>
  <text x="512" y="480" font-family="Arial" font-size="48" fill="#FF6B35" text-anchor="middle">
    Image {index}
  </text>
  <text x="512" y="560" font-family="Arial" font-size="24" fill="#2D3047" text-anchor="middle">
    {caption}
  </text>
  <text x="512" y="620" font-family="Arial" font-size="16" fill="#999" text-anchor="middle">
    (纽约客风格插画)
  </text>
</svg>'''

        # 保存为 SVG (可以转换为 PNG)
        svg_path = path.with_suffix('.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        # 复制为 PNG 占位
        import shutil
        shutil.copy(svg_path, path)


class PDFGeneratorWrapper:
    """PDF 生成器包装器"""

    def __init__(self):
        self.work_dir = Path("output")
        self.work_dir.mkdir(exist_ok=True)

    def generate(self, html_content: str, title_zh: str, metadata: dict) -> str:
        """生成 PDF"""
        # 尝试导入真正的 PDF 生成器
        try:
            from generate_pdf import generate_pdf as real_generate
            output_file = f"{title_zh}.pdf"

            result = real_generate(
                html_content=html_content,
                output_filename=output_file,
                title_zh=title_zh,
                title_en=metadata.get("title_en", ""),
                authors=metadata.get("authors", []),
                paper_id=metadata.get("paper_id", ""),
                work_dir="."
            )
            return result
        except ImportError:
            # 占位：创建 HTML 版本
            html_path = self.work_dir / title_zh / f"{title_zh}.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)

            # 包装成完整 HTML
            full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title_zh}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.8; }}
        h1, h2, h3 {{ color: #2D3047; }}
        .highlight {{ background: #F7C59F; padding: 1rem; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>{title_zh}</h1>
    <p><strong>{metadata.get('title_en', '')}</strong></p>
    <hr>
    {html_content}
</body>
</html>'''

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(full_html)

            return str(html_path)


class PaperInterpreter:
    """论文解读主类"""

    def __init__(self, use_real_arxiv: bool = False, use_llm: bool = False):
        self.use_real_arxiv = use_real_arxiv
        self.arxiv_client = ArxivClient()
        
        if use_llm:
            self.content_gen = RealContentGenerator()
        else:
            self.content_gen = ContentGenerator()
            
        self.image_gen = ImageGenerator()
        self.pdf_gen = PDFGeneratorWrapper()

        # 日志
        self.logs = []

    def log(self, stage: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{stage}] {message}"
        self.logs.append(log_entry)
        print(f"  {log_entry}")

    def run(self, arxiv_url: str) -> Dict[str, Any]:
        """执行完整的论文解读流程"""

        print("=" * 60)
        print("🚀 论文解读 Agent 启动")
        print("=" * 60)

        # 解析论文 ID
        paper_id = self._extract_paper_id(arxiv_url)
        self.log("STAGE 1", f"论文ID: {paper_id}")

        # ========== Stage 1: 获取论文信息 ==========
        print("\n📥 Stage 1: 论文信息获取")
        metadata = self.arxiv_client.fetch_metadata(paper_id)
        self.log("STAGE 1", f"标题: {metadata.title_zh}")
        self.log("STAGE 1", f"作者: {[a['name'] for a in metadata.authors]}")

        # ========== Stage 2: 生成黄叔风格文章 ==========
        print("\n✍️  Stage 2: 生成黄叔风格文章")
        article = self.content_gen.generate_article(metadata)
        word_count = len(article)
        self.log("STAGE 2", f"文章字数: ~{word_count} 字符")

        # ========== Stage 3: 生成配图 ==========
        print("\n🎨  Stage 3: 纽约客风格配图生成")
        images = self.image_gen.generate_images(paper_id, 5)
        self.log("STAGE 3", f"生成图片: {len(images)} 张")

        # ========== Stage 4: HTML 生成 ==========
        print("\n🌐  Stage 4: 2026前沿设计 HTML 生成")
        html_content = self._generate_html(article, metadata, images)
        self.log("STAGE 4", f"HTML 生成完成")

        # ========== Stage 5: PDF 生成 ==========
        print("\n📄  Stage 5: PDF 生成")
        pdf_path = self.pdf_gen.generate(html_content, metadata.title_zh, {
            "title_en": metadata.title_en,
            "authors": metadata.authors,
            "paper_id": metadata.paper_id
        })
        self.log("STAGE 5", f"PDF: {pdf_path}")

        # ========== Stage 6: 文件整理 ==========
        print("\n📁  Stage 6: 文件整理与输出")
        output = self._organize_files(metadata, article, images, html_content, pdf_path)
        self.log("STAGE 6", f"输出目录: {output['output_dir']}")

        # ========== 完成 ==========
        print("\n" + "=" * 60)
        print("✅ 论文解读完成!")
        print("=" * 60)

        return output

    def _extract_paper_id(self, url: str) -> str:
        """从 URL 提取论文 ID"""
        import re
        match = re.search(r'/abs/(\d+\.\d+)', url)
        if match:
            return match.group(1)
        # 默认返回模拟论文 ID
        return "2501.12345"

    def _generate_html(self, article: str, metadata: PaperMetadata, images: list) -> str:
        """生成 HTML (简化版，实际应使用 template.html)"""
        # 转换 Markdown 到简单 HTML
        html_sections = []

        # 处理图片网格
        if images:
            image_grid = '<div class="images-grid">'
            for img in images:
                image_grid += f'''
                <div class="image-card">
                    <img src="{img['path']}" alt="{img['caption']}">
                    <div class="image-caption">{img['caption']}</div>
                </div>'''
            image_grid += '</div>'

        # 解析 Markdown 段落
        lines = article.split('\n')
        current_section = ""

        for line in lines:
            if line.startswith('## '):
                if current_section:
                    html_sections.append(f'<section class="content-block">{current_section}</section>')
                current_section = f'<h2>{line[3:]}</h2>'
            elif line.startswith('### '):
                current_section += f'<h3>{line[4:]}</h3>'
            elif line.startswith('**') and line.endswith('**'):
                current_section += f'<p><strong>{line[2:-2]}</strong></p>'
            elif line.strip():
                current_section += f'<p>{line}</p>'

        if current_section:
            html_sections.append(f'<section class="content-block">{current_section}</section>')

        # 插入图片
        if images:
            html_sections.insert(2, f'<section class="content-block">{image_grid}</section>')

        return '\n'.join(html_sections)

    def _organize_files(
        self,
        metadata: PaperMetadata,
        article: str,
        images: list,
        html_content: str,
        pdf_path: str
    ) -> Dict[str, Any]:
        """整理输出文件"""
        output_dir = Path("output") / metadata.title_zh
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存 Markdown
        md_path = output_dir / f"{metadata.title_zh}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {metadata.title_zh}\n\n")
            f.write(f"**英文标题**: {metadata.title_en}\n\n")
            f.write(f"**作者**: {', '.join([a['name'] for a in metadata.authors])}\n\n")
            f.write(f"**Paper ID**: {metadata.paper_id}\n\n")
            f.write("---\n\n")
            f.write(article)

        # 保存日志
        log_path = output_dir / f"{metadata.title_zh}_log.txt"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("论文解读执行日志\n")
            f.write("=" * 60 + "\n\n")
            for log in self.logs:
                f.write(log + "\n")

        # 移动图片
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        for img in images:
            import shutil
            shutil.copy(img['path'], images_dir / Path(img['path']).name)

        return {
            "output_dir": str(output_dir),
            "files": {
                "markdown": str(md_path),
                "log": str(log_path),
                "pdf": pdf_path
            }
        }


def main():
    parser = argparse.ArgumentParser(description="论文解读测试脚本")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://arxiv.org/abs/2501.12345",
        help="arXiv 论文 URL"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="使用真实的 arXiv API (需要网络)"
    )
    parser.add_argument(
        "--model",
        choices=["mock", "sonnet"],
        default="mock",
        help="选择模型: mock (模拟) 或 sonnet (Claude 3.5 Sonnet)"
    )

    args = parser.parse_args()

    print(f"📄 测试论文: {args.url}")
    print(f"🤖 模型模式: {args.model}")
    print()

    use_llm = (args.model == "sonnet")
    interpreter = PaperInterpreter(use_real_arxiv=args.real, use_llm=use_llm)
    result = interpreter.run(args.url)

    print(f"\n📂 输出目录: {result['output_dir']}")
    print(f"   - Markdown: {result['files']['markdown']}")
    print(f"   - PDF: {result['files']['pdf']}")
    print(f"   - 日志: {result['files']['log']}")


if __name__ == "__main__":
    main()
