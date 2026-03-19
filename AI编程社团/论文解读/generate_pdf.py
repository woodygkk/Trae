#!/usr/bin/env python3
"""
generate_pdf.py - ArXiv 论文解读 PDF 生成器

功能:
- HTML 转 PDF
- 中文字体支持 (自动下载 NotoSansSC)
- 封面页生成
- 目录生成
- 高亮框、引用框样式
- 响应式布局

依赖:
- playwright
- weasyprint (可选替代方案)
"""

import os
import sys
import json
import re
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.request import urlretrieve
from urllib.error import URLError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF 生成器类"""

    def __init__(self, work_dir: str = "."):
        self.work_dir = Path(work_dir)
        self.output_dir = self.work_dir / "output"
        self.tmp_dir = self.work_dir / "tmp"
        self.fonts_dir = self.work_dir / "fonts"

        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.fonts_dir.mkdir(parents=True, exist_ok=True)

        # 字体配置
        self.font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
        self.font_path = self.fonts_dir / "NotoSansSC-Regular.otf"

        # 配色方案 (与 template.html 保持一致)
        self.colors = {
            "primary": "#FF6B35",
            "secondary": "#F7C59F",
            "dark": "#2D3047",
            "light": "#EFEFD0"
        }

    def download_font(self) -> bool:
        """下载中文字体"""
        if self.font_path.exists():
            logger.info(f"字体已存在: {self.font_path}")
            return True

        logger.info("正在下载 NotoSansSC 字体...")

        try:
            # 创建临时文件
            temp_path = self.tmp_dir / "font_download.otf"

            # 下载字体
            urlretrieve(self.font_url, temp_path)

            # 验证文件
            if temp_path.stat().st_size > 1_000_000:  # 至少 1MB
                temp_path.rename(self.font_path)
                logger.info(f"字体下载成功: {self.font_path}")
                return True
            else:
                logger.warning("字体文件过小，下载可能失败")
                return False

        except URLError as e:
            logger.error(f"下载字体失败: {e}")
            return False

    def ensure_font(self) -> str:
        """确保字体可用，返回字体路径"""
        if not self.download_font():
            # 回退到系统字体
            return self._get_system_font()
        return str(self.font_path)

    def _get_system_font(self) -> str:
        """获取系统可用的中文字体"""
        system_fonts = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑 (Windows)
            "/System/Library/Fonts/PingFang.ttc",  # 苹方 (macOS)
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux
        ]

        for font_path in system_fonts:
            if Path(font_path).exists():
                return font_path

        logger.warning("未找到中文字体，PDF 中的中文可能无法正确显示")
        return ""

    def parse_html_for_toc(self, html_content: str) -> List[Dict[str, str]]:
        """解析 HTML 提取目录结构"""
        toc = []
        # 匹配 h2, h3 标题
        pattern = r'<h([23])[^>]*>(.*?)</h\1>'
        matches = re.findall(pattern, html_content, re.DOTALL)

        for level, title in matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if clean_title:
                toc.append({
                    "level": int(level),
                    "title": clean_title
                })

        return toc

    def wrap_content_with_template(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """将内容包装成完整的 HTML 模板"""
        font_path = self.ensure_font()

        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{metadata.get('title_zh', '论文解读')}</title>
    <style>
        @font-face {{
            font-family: 'NotoSansSC';
            src: url('file://{font_path}') format('opentype');
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'NotoSansSC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #2D3047;
            padding: 2cm;
        }}

        /* 封面页 */
        .cover-page {{
            page-break-after: always;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #FFFAF6 0%, #F7C59F 100%);
        }}

        .cover-page h1 {{
            font-size: 28pt;
            color: #2D3047;
            margin-bottom: 1.5cm;
            line-height: 1.3;
            max-width: 80%;
        }}

        .cover-page .subtitle {{
            font-size: 14pt;
            color: #FF6B35;
            margin-bottom: 3cm;
        }}

        .cover-page .meta {{
            font-size: 11pt;
            color: #666;
            line-height: 2;
        }}

        .cover-page .paper-id {{
            margin-top: 2cm;
            font-size: 10pt;
            color: #999;
        }}

        /* 目录页 */
        .toc-page {{
            page-break-after: always;
        }}

        .toc-title {{
            font-size: 18pt;
            font-weight: bold;
            color: #2D3047;
            margin-bottom: 1cm;
            padding-bottom: 0.5cm;
            border-bottom: 2px solid #FF6B35;
        }}

        .toc-item {{
            padding: 0.3cm 0;
            font-size: 11pt;
            display: flex;
            align-items: baseline;
        }}

        .toc-item.level-2 {{ margin-left: 0.5cm; }}
        .toc-item.level-3 {{ margin-left: 1cm; }}

        .toc-dots {{
            flex-grow: 1;
            border-bottom: 1px dotted #ccc;
            margin: 0 0.5cm;
            transform: translateY(-4px);
        }}

        .toc-page {{
            font-family: 'NotoSansSC', sans-serif;
        }}

        /* 内容区域 */
        .content {{
            font-size: 11pt;
            line-height: 1.8;
        }}

        h2 {{
            font-size: 16pt;
            color: #2D3047;
            margin: 1.5cm 0 1cm;
            padding-left: 0.5cm;
            border-left: 4px solid #FF6B35;
        }}

        h3 {{
            font-size: 13pt;
            color: #2D3047;
            margin: 1.2cm 0 0.8cm;
        }}

        p {{
            margin-bottom: 0.8cm;
            text-align: justify;
        }}

        /* 高亮框 */
        .highlight-box {{
            background: linear-gradient(135deg, #FF6B35 0%, #ff8c5a 100%);
            color: white;
            padding: 1cm;
            border-radius: 8px;
            margin: 1.5cm 0;
            page-break-inside: avoid;
        }}

        .highlight-box h4 {{
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.9;
            margin-bottom: 0.5cm;
        }}

        /* 引用框 */
        .citation-box {{
            background: #EFEFD0;
            border-left: 4px solid #2D3047;
            padding: 0.8cm 1cm;
            margin: 1.5cm 0;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
        }}

        .citation-box p {{
            margin-bottom: 0;
            font-style: italic;
            font-size: 10pt;
        }}

        /* 类比框 */
        .analogy-box {{
            background: linear-gradient(135deg, #F7C59F 0%, #fff 50%);
            border-radius: 8px;
            padding: 1cm;
            margin: 1.5cm 0;
            page-break-inside: avoid;
        }}

        .analogy-box h4 {{
            color: #FF6B35;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5cm;
        }}

        /* 图片 */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1cm auto;
        }}

        .image-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8cm;
            margin: 1.5cm 0;
        }}

        .image-grid img {{
            margin: 0;
        }}

        .image-caption {{
            font-size: 9pt;
            color: #666;
            text-align: center;
            margin-top: 0.3cm;
        }}

        /* 层级解释 */
        .layer-explanation {{
            margin: 1cm 0;
            padding-left: 0.8cm;
            border-left: 2px solid #F7C59F;
        }}

        .layer-label {{
            display: inline-block;
            font-size: 8pt;
            padding: 0.15cm 0.5cm;
            border-radius: 15px;
            margin-bottom: 0.3cm;
            font-weight: bold;
        }}

        .layer-1 {{ border-color: #4CAF50; }}
        .layer-1 .layer-label {{ background: #E8F5E9; color: #2E7D32; }}

        .layer-2 {{ border-color: #2196F3; }}
        .layer-2 .layer-label {{ background: #E3F2FD; color: #1565C0; }}

        .layer-3 {{ border-color: #9C27B0; }}
        .layer-3 .layer-label {{ background: #F3E5F5; color: #7B1FA2; }}

        /* 摘要框 */
        .abstract-box {{
            background: #F5F5F5;
            padding: 1cm;
            border-radius: 8px;
            margin: 1.5cm 0;
        }}

        .abstract-box h4 {{
            font-size: 10pt;
            color: #666;
            margin-bottom: 0.5cm;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        /* 影响卡片 */
        .impact-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8cm;
            margin: 1.5cm 0;
        }}

        .impact-card {{
            background: white;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 0.8cm;
            text-align: center;
        }}

        .impact-icon {{
            font-size: 24pt;
            margin-bottom: 0.3cm;
        }}

        .impact-card h4 {{
            font-size: 11pt;
            margin-bottom: 0.3cm;
        }}

        .impact-card p {{
            font-size: 9pt;
            color: #666;
            margin-bottom: 0;
        }}

        /* 总结框 */
        .summary-box {{
            background: linear-gradient(135deg, #2D3047 0%, #4a4f6e 100%);
            color: white;
            border-radius: 8px;
            padding: 1.5cm;
            margin: 2cm 0;
            text-align: center;
        }}

        .summary-box h3 {{
            font-size: 14pt;
            margin-bottom: 1cm;
            border: none;
            padding: 0;
            color: white;
        }}

        .takeaways {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5cm;
            margin-top: 1cm;
        }}

        .takeaway {{
            background: rgba(255, 255, 255, 0.15);
            padding: 0.4cm 0.8cm;
            border-radius: 20px;
            font-size: 10pt;
        }}

        /* 页脚 */
        .footer {{
            position: fixed;
            bottom: 1cm;
            left: 2cm;
            right: 2cm;
            text-align: center;
            font-size: 9pt;
            color: #999;
        }}

        @page {{
            margin: 0;
            @bottom-right {{
                content: counter(page);
                font-size: 9pt;
                color: #999;
            }}
        }}
    </style>
</head>
<body>
    <!-- 封面页 -->
    <div class="cover-page">
        <h1>{metadata.get('title_zh', '论文解读')}</h1>
        <p class="subtitle">{metadata.get('title_en', '')}</p>
        <div class="meta">
            {"<br>".join([f"{a.get('name', '')} ({a.get('institution', '')})" for a in metadata.get('authors', [])])}
            <br><br>
            {metadata.get('date', datetime.now().strftime('%Y-%m-%d'))}
        </div>
        <p class="paper-id">arXiv:{metadata.get('paper_id', 'N/A')}</p>
    </div>

    <!-- 目录页 -->
    <div class="toc-page">
        <h2 class="toc-title">目录</h2>
        {self._generate_toc_html(metadata.get('toc', []))}
    </div>

    <!-- 内容页 -->
    <div class="content">
        {content}
    </div>
</body>
</html>'''

        return html_template

    def _generate_toc_html(self, toc: List[Dict[str, str]]) -> str:
        """生成目录 HTML"""
        if not toc:
            return '<p style="color:#999;">无目录</p>'

        html_parts = []
        for item in toc:
            level_class = f"level-{item.get('level', 2)}"
            html_parts.append(
                f'<div class="toc-item {level_class}">'
                f'<span>{item.get("title", "")}</span>'
                f'<span class="toc-dots"></span>'
                f'<span>{len(html_parts) + 1}</span>'
                f'</div>'
            )

        return ''.join(html_parts)

    def convert_to_pdf(
        self,
        html_content: str,
        output_filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        将 HTML 转换为 PDF

        Args:
            html_content: HTML 内容
            output_filename: 输出文件名 (不含路径)
            metadata: 元数据字典

        Returns:
            输出文件的完整路径
        """
        # 包装内容
        full_html = self.wrap_content_with_template(html_content, metadata)

        # 保存临时 HTML 文件
        temp_html = self.tmp_dir / "temp_content.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(full_html)
            logger.info(f"临时 HTML 已保存: {temp_html}")

        # 输出路径
        output_path = self.output_dir / metadata.get('title_zh', 'output') / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 尝试使用 Playwright
        try:
            return self._convert_with_playwright(temp_html, output_path)
        except ImportError:
            logger.warning("Playwright 不可用，尝试使用 WeasyPrint...")
            try:
                return self._convert_with_weasyprint(temp_html, output_path)
            except ImportError:
                logger.warning("WeasyPrint 不可用，尝试使用 pdfkit...")
                return self._convert_with_pdfkit(temp_html, output_path)

    def _convert_with_playwright(self, html_path: Path, output_path: Path) -> str:
        """使用 Playwright 转换 PDF"""
        from playwright.sync_api import sync_playwright

        logger.info("正在使用 Playwright 生成 PDF...")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # 加载 HTML
            page.goto(f"file://{html_path.absolute()}", wait_until="networkidle")

            # 生成 PDF
            page.pdf(
                path=str(output_path),
                format="A4",
                margin={
                    "top": "2cm",
                    "right": "2cm",
                    "bottom": "2cm",
                    "left": "2cm"
                },
                print_background=True,
                display_header_footer=True,
                header_template="",
                footer_template=""
            )

            browser.close()

        logger.info(f"PDF 生成成功: {output_path}")
        return str(output_path)

    def _convert_with_weasyprint(self, html_path: Path, output_path: Path) -> str:
        """使用 WeasyPrint 转换 PDF"""
        from weasyprint import HTML, CSS

        logger.info("正在使用 WeasyPrint 生成 PDF...")

        html = HTML(filename=str(html_path))
        html.write_pdf(str(output_path))

        logger.info(f"PDF 生成成功: {output_path}")
        return str(output_path)

    def _convert_with_pdfkit(self, html_path: Path, output_path: Path) -> str:
        """使用 pdfkit 转换 PDF"""
        import pdfkit

        logger.info("正在使用 pdfkit 生成 PDF...")

        options = {
            'page-size': 'A4',
            'margin-top': '2cm',
            'margin-right': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }

        pdfkit.from_file(str(html_path), str(output_path), options=options)

        logger.info(f"PDF 生成成功: {output_path}")
        return str(output_path)

    def cleanup(self):
        """清理临时文件"""
        if self.tmp_dir.exists():
            import shutil
            shutil.rmtree(self.tmp_dir)
            logger.info("临时文件已清理")


def generate_pdf(
    html_content: str,
    output_filename: str,
    title_zh: str,
    title_en: str = "",
    authors: List[Dict[str, str]] = None,
    paper_id: str = "",
    date: str = "",
    work_dir: str = "."
) -> str:
    """
    便捷的 PDF 生成函数

    Args:
        html_content: HTML 内容
        output_filename: 输出文件名
        title_zh: 中文标题
        title_en: 英文标题
        authors: 作者列表
        paper_id: 论文 ID
        date: 日期
        work_dir: 工作目录

    Returns:
        输出文件的路径
    """
    generator = PDFGenerator(work_dir)

    metadata = {
        "title_zh": title_zh,
        "title_en": title_en,
        "authors": authors or [],
        "paper_id": paper_id,
        "date": date or datetime.now().strftime('%Y-%m-%d'),
        "toc": generator.parse_html_for_toc(html_content)
    }

    output_path = generator.convert_to_pdf(html_content, output_filename, metadata)

    # 可选：清理临时文件
    # generator.cleanup()

    return output_path


# CLI 入口点
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成论文解读 PDF")
    parser.add_argument("html_file", help="HTML 文件路径")
    parser.add_argument("-o", "--output", default="output.pdf", help="输出文件名")
    parser.add_argument("--title-zh", required=True, help="中文标题")
    parser.add_argument("--title-en", default="", help="英文标题")
    parser.add_argument("--paper-id", default="", help="论文 ID")
    parser.add_argument("--authors", default="[]", help="作者 JSON 数组")
    parser.add_argument("--work-dir", default=".", help="工作目录")

    args = parser.parse_args()

    # 读取 HTML 内容
    with open(args.html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 解析作者
    try:
        authors = json.loads(args.authors)
    except json.JSONDecodeError:
        authors = []

    # 生成 PDF
    output_path = generate_pdf(
        html_content=html_content,
        output_filename=args.output,
        title_zh=args.title_zh,
        title_en=args.title_en,
        authors=authors,
        paper_id=args.paper_id,
        work_dir=args.work_dir
    )

    print(f"✅ PDF 已生成: {output_path}")
