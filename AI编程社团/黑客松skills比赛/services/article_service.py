# -*- coding: utf-8 -*-
"""
文章服务
保存和管理生成的文章
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# 导入配图服务
try:
    from services.image_service import ImageService
except ImportError:
    ImageService = None


class ArticleService:
    """文章服务"""

    def __init__(self, output_dir: str = "output/articles"):
        self.output_dir = output_dir
        self._ensure_dir()

    def _ensure_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_article(self, topic: str, platform: str, content: str) -> str:
        """
        保存文章到本地文件

        Args:
            topic: 话题标题
            platform: 来源平台
            content: 文章内容

        Returns:
            保存的文件路径
        """
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (" ", "-", "_")).strip()[:20]
        filename = f"{timestamp}_{safe_topic}.md"
        filepath = os.path.join(self.output_dir, filename)

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n")
            f.write(f"> 来源平台: {platform}\n\n")
            f.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(content)

        print(f"文章已保存到: {filepath}")

        # 自动生成配图
        self._generate_cover(topic, content, filepath)

        return filepath

    def _generate_cover(self, topic: str, content: str, article_path: str):
        """为文章生成配图"""
        if ImageService is None:
            return

        try:
            image_service = ImageService()
            # 生成配图
            result = image_service.generate_for_article(article_path)
            if result:
                print(f"配图已生成: {result}")
        except Exception as e:
            print(f"生成配图时出错: {e}")

    def list_articles(self) -> List[Dict]:
        """
        列出所有已生成的文章

        Returns:
            文章列表，每条包含 filepath, topic, created_at
        """
        articles = []

        if not os.path.exists(self.output_dir):
            return articles

        for filename in os.listdir(self.output_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.output_dir, filename)

                # 读取文章第一行作为标题
                with open(filepath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        topic = first_line[2:]
                    else:
                        topic = filename

                # 获取文件创建时间
                created_at = datetime.fromtimestamp(os.path.getctime(filepath))

                articles.append({
                    "filepath": filepath,
                    "topic": topic,
                    "created_at": created_at.strftime("%Y-%m-%d %H:%M"),
                    "filename": filename
                })

        # 按时间倒序排列
        articles.sort(key=lambda x: x["created_at"], reverse=True)
        return articles

    def read_article(self, filepath: str) -> Optional[str]:
        """
        读取文章内容

        Args:
            filepath: 文章文件路径

        Returns:
            文章内容，如果文件不存在返回 None
        """
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}")
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def delete_article(self, filepath: str) -> bool:
        """
        删除文章

        Args:
            filepath: 文章文件路径

        Returns:
            是否删除成功
        """
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}")
            return False

        try:
            os.remove(filepath)
            print(f"已删除: {filepath}")
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False


if __name__ == "__main__":
    # 测试
    service = ArticleService()
    articles = service.list_articles()
    print(f"共有 {len(articles)} 篇文章")
    for a in articles[:5]:
        print(f"- {a['topic']} ({a['created_at']})")
