# -*- coding: utf-8 -*-
"""
配图服务
使用MiniMax文生图API为文章生成配图
"""

import os
import re
import requests
from typing import Optional, Tuple
from datetime import datetime

# 尝试导入config，如果失败则使用默认值
try:
    from config import MINIMAX_API_KEY, MINIMAX_API_BASE
except ImportError:
    MINIMAX_API_KEY = ""
    MINIMAX_API_BASE = "https://api.minimax.chat/v1"


class ImageService:
    """配图服务"""

    def __init__(self, output_dir: str = "E:/学习资料/AI编程课/Trae/AI编程社团/黑客松skills比赛/文生图"):
        self.output_dir = output_dir
        self.api_key = MINIMAX_API_KEY
        self.api_base = MINIMAX_API_BASE
        self._ensure_dir()

    def _ensure_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def analyze_content(self, title: str, content: str) -> str:
        """
        分析文章内容，提取关键词用于生成图片

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            用于生成图片的提示词
        """
        if not self.api_key:
            return f"封面图片，主题：{title}，简约现代风格，适合公众号"

        # 使用AI提取图片提示词
        url = f"{self.api_base}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""根据以下文章标题和内容，生成一个适合的AI绘图提示词，用于生成公众号封面图。

标题：{title}

内容摘要：{content[:500]}

要求：
- 简洁描述画面内容
- 风格：现代简约、扁平化设计、适合文章配图
- 不要包含文字
- 50字以内

直接输出提示词，不要其他内容。"""

        payload = {
            "model": "abab6.5s-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                prompt_result = data["choices"][0]["message"]["content"].strip()
                return prompt_result
        except Exception as e:
            print(f"  分析内容失败，使用默认提示词: {e}")

        # 默认提示词
        return f"封面图片，主题：{title}，简约现代风格，适合公众号"

    def generate_image(self, prompt: str, filename: str) -> Optional[str]:
        """
        调用MiniMax文生图API生成图片

        Args:
            prompt: 图片提示词
            filename: 保存的文件名

        Returns:
            保存的图片路径，失败返回None
        """
        if not self.api_key:
            print("  未配置MiniMax API密钥，无法生成图片")
            return None

        url = f"{self.api_base}/image_generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建提示词（英文更适合AI绘图）
        enhanced_prompt = f"{prompt}, flat illustration, modern style, clean background, high quality, WeChat cover"

        # MiniMax 文生图模型 - 尝试多个可能的模型名称
        models_to_try = ["minimax-image-01", "minimax-image-01-v1", "image-01"]
        payload = None

        for model_name in models_to_try:
            payload = {
                "model": model_name,
                "prompt": enhanced_prompt,
                "aspect_ratio": "16:9",
                "num_images": 1
            }
            # 测试这个模型是否可用
            test_response = requests.post(url, headers=headers, json=payload, timeout=60)
            test_data = test_response.json()

            if test_data.get("base_resp", {}).get("status_code") != 2013:
                # 模型可用，使用这个
                print(f"  使用模型: {model_name}")
                break
            else:
                print(f"  模型 {model_name} 不可用，尝试下一个...")
                payload = None

        if payload is None:
            print("  所有模型都不可用，尝试通用配置...")
            payload = {
                "model": "image-01",
                "prompt": enhanced_prompt,
                "num_images": 1
            }

        try:
            print(f"  正在生成配图...")
            print(f"  提示词: {prompt[:50]}...")

            response = requests.post(url, headers=headers, json=payload, timeout=120)
            data = response.json()

            print(f"  API响应: {data}")

            # 解析返回的图片URL - MiniMax可能返回不同的格式
            image_url = None

            # 尝试格式1: data[0].url
            if "data" in data and isinstance(data["data"], dict):
                # data.data.image_urls (新版格式)
                if "image_urls" in data["data"]:
                    image_urls = data["data"]["image_urls"]
                    if isinstance(image_urls, list) and len(image_urls) > 0:
                        image_url = image_urls[0]

            # 尝试格式2: data[0].url (旧版格式)
            if not image_url and "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                image_url = data["data"][0].get("url")

            # 尝试格式3: image_url 字段
            if not image_url and "image_url" in data:
                image_url = data.get("image_url")

            if image_url:
                # 下载图片并保存
                return self._download_and_save(image_url, filename)

            # 检查错误信息
            if "base_resp" in data:
                status_msg = data["base_resp"].get("status_msg", "")
                print(f"  API返回: {status_msg}")
            elif "error" in data:
                print(f"  API错误: {data.get('error')}")

            print(f"  生成图片失败")
            return None

        except requests.exceptions.Timeout:
            print("  请求超时，请重试")
            return None
        except Exception as e:
            print(f"  生成图片失败: {e}")
            return None

    def _download_and_save(self, image_url: str, filename: str) -> Optional[str]:
        """
        下载图片并保存

        Args:
            image_url: 图片URL
            filename: 保存的文件名

        Returns:
            保存的文件路径
        """
        try:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()

            # 确保文件名有扩展名
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                filename += ".png"

            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"  图片已保存到: {filepath}")
            return filepath

        except Exception as e:
            print(f"  下载图片失败: {e}")
            return None

    def generate_for_article(self, article_path: str) -> Optional[str]:
        """
        为已有文章生成配图

        Args:
            article_path: 文章文件路径

        Returns:
            生成的图片路径
        """
        # 读取文章内容
        if not os.path.exists(article_path):
            print(f"文章文件不存在: {article_path}")
            return None

        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取标题（第一行 # 后的内容）
        title = "文章封面"
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # 提取正文内容（去除元信息）
        body_content = ""
        in_body = False
        for line in lines:
            if line.startswith('---'):
                in_body = True
                continue
            if in_body and line.strip() and not line.startswith('>') and not line.startswith('#'):
                body_content += line + " "

        if not body_content:
            body_content = content[:500]

        # 生成图片
        print(f"\n为文章生成配图: {title}")

        # 分析内容生成提示词
        prompt = self.analyze_content(title, body_content)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()[:20]
        filename = f"{timestamp}_{safe_title}.png"

        return self.generate_image(prompt, filename)


def generate_cover_for_article(title: str, content: str, output_path: str = None) -> Optional[str]:
    """
    为文章生成封面图的便捷函数

    Args:
        title: 文章标题
        content: 文章内容
        output_path: 可选的输出路径

    Returns:
        生成的图片路径
    """
    service = ImageService()

    # 分析内容生成提示词
    prompt = service.analyze_content(title, content)

    # 生成文件名
    if output_path:
        filename = os.path.basename(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()[:20]
        filename = f"{timestamp}_{safe_title}.png"

    return service.generate_image(prompt, filename)


if __name__ == "__main__":
    # 测试
    service = ImageService()
    print("配图服务测试")
    print(f"输出目录: {service.output_dir}")

    # 测试生成
    result = service.generate_for_article("output/articles/20260214_112259_AI技术发展.md")
    if result:
        print(f"生成成功: {result}")
    else:
        print("生成失败")
