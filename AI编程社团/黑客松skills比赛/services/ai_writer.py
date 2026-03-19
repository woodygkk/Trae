# -*- coding: utf-8 -*-
"""
AI写作服务
调用大模型API生成公众号文章
"""

import os
import requests
from typing import Optional
from config import AI_PROVIDER, OPENAI_API_KEY, CLAUDE_API_KEY, MINIMAX_API_KEY, MINIMAX_API_BASE, ARTICLE_WORD_COUNT, WRITING_STYLE


class AIWriter:
    """AI写作服务"""

    def __init__(self):
        self.article_word_count = ARTICLE_WORD_COUNT
        self.writing_style = WRITING_STYLE

    def generate_article(self, topic: str, platform: str) -> str:
        """
        根据话题生成公众号文章

        Args:
            topic: 话题标题
            platform: 来源平台

        Returns:
            生成的完整文章内容
        """
        print(f"正在使用AI生成文章，关于: {topic}...")

        if AI_PROVIDER == "openai":
            return self._generate_with_openai(topic, platform)
        elif AI_PROVIDER == "claude":
            return self._generate_with_claude(topic, platform)
        elif AI_PROVIDER in ["minimax", "minimax2.5"]:
            return self._generate_with_minimax(topic, platform)
        else:
            return self._generate_with_openai(topic, platform)

    def _generate_with_openai(self, topic: str, platform: str) -> str:
        """使用OpenAI API生成文章"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)

            prompt = self._build_prompt(topic, platform)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个资深的自媒体博主，擅长写爆款文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )

            article = response.choices[0].message.content
            print("文章生成完成！")
            return article

        except ImportError:
            print("请先安装 openai 库: pip install openai")
            return self._get_sample_article(topic, platform)
        except Exception as e:
            print(f"OpenAI API 调用失败: {e}")
            return self._get_sample_article(topic, platform)

    def _generate_with_claude(self, topic: str, platform: str) -> str:
        """使用Claude API生成文章"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

            prompt = self._build_prompt(topic, platform)

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                system="你是一个资深的自媒体博主，擅长写爆款公众号文章。",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            article = message.content[0].text
            print("文章生成完成！")
            return article

        except ImportError:
            print("请先安装 anthropic 库: pip install anthropic")
            return self._get_sample_article(topic, platform)
        except Exception as e:
            print(f"Claude API 调用失败: {e}")
            return self._get_sample_article(topic, platform)

    def _generate_with_minimax(self, topic: str, platform: str) -> str:
        """使用MiniMax API生成文章（分段生成，避免截断）"""
        try:
            url = f"{MINIMAX_API_BASE}/text/chatcompletion_v2"
            headers = {
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            }

            print("  正在生成标题...")
            # 第一步：生成标题（精简prompt）
            title_prompt = f'给"{topic}"写3个公众号标题，简洁有力'
            title_payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {"role": "user", "content": title_prompt}
                ],
                "max_tokens": 150
            }
            response = requests.post(url, headers=headers, json=title_payload, timeout=60)
            data = response.json()
            titles = ""
            if "choices" in data and len(data["choices"]) > 0:
                titles = data["choices"][0]["message"]["content"]

            print("  正在生成开头...")
            # 第二步：生成开头（精简prompt）
            intro_prompt = f'写一个公众号开头，主题是"{topic}"，50字，亲切有趣'
            intro_payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {"role": "user", "content": intro_prompt}
                ],
                "max_tokens": 300
            }
            response = requests.post(url, headers=headers, json=intro_payload, timeout=60)
            data = response.json()
            intro = ""
            if "choices" in data and len(data["choices"]) > 0:
                intro = data["choices"][0]["message"]["content"]

            print("  正在生成中间内容...")
            # 第三步：生成中间内容（精简prompt）
            content_prompt = f'给公众号写中间内容，主题"{topic}"，3个观点，各50字'
            content_payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {"role": "user", "content": content_prompt}
                ],
                "max_tokens": 500
            }
            response = requests.post(url, headers=headers, json=content_payload, timeout=60)
            data = response.json()
            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]

            print("  正在生成结尾...")
            # 第四步：生成结尾（精简prompt）
            ending_prompt = f'写公众号结尾，主题"{topic}"，30字，引导评论'
            ending_payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {"role": "user", "content": ending_prompt}
                ],
                "max_tokens": 200
            }
            response = requests.post(url, headers=headers, json=ending_payload, timeout=60)
            data = response.json()
            ending = ""
            if "choices" in data and len(data["choices"]) > 0:
                ending = data["choices"][0]["message"]["content"]

            # 检查内容是否被截断（太短）
            total_length = len(titles) + len(intro) + len(content) + len(ending)
            print(f"  生成内容长度: {total_length}")
            if total_length < 600:
                # 内容太短，使用高质量模板
                print("  API返回内容较短，使用优化模板...")
                return self._get_sample_article(topic, platform)

            # 合并所有内容
            article = f"""标题：{titles}

---

{intro}

---

{content}

---

{ending}"""

            print("文章生成完成！")
            return article

        except Exception as e:
            print(f"MiniMax API 调用失败: {e}")
            return self._get_sample_article(topic, platform)

    def _build_prompt(self, topic: str, platform: str) -> str:
        """构建生成文章的提示词"""
        prompt = f"""请帮我写一篇公众号文章，主题是：{topic}（来自{platform}热门）

要求：
1. 字数约{self.article_word_count}字
2. {self.writing_style}
3. 文章结构：
   - 一个吸引眼球的标题
   - 开头用一个有趣的故事或现象引入
   - 中间部分提供3-5个干货观点或实用信息
   - 结尾引导互动（提问、评论等）
4. 语言风格要适合公众号阅读，容易引发共鸣和转发
5. 可以适当添加emoji表情
6. 段落之间要留空行，便于阅读

请直接输出文章内容，不需要其他说明。"""
        return prompt

    def _get_sample_article(self, topic: str, platform: str) -> str:
        """当API不可用时，返回示例文章（拟人化风格）"""
        article = f"""
救命！{topic}也太火了吧！！

姐妹们！今天刷微博的时候，我发现{topic}彻底刷屏了！！
刚开始我还想不就是个话题吗，至于这么夸张吗？
结果好家伙，点进去一看，好多人在讨论，我也忍不住加入了混战...

说实话，我刚开始真的不理解，为啥这个话题能这么火？
直到我翻了差不多100条评论，才搞明白是咋回事。

首先吧，我觉得是因为这件事真的戳到大家痛点了。
你想想，现在大家压力都挺大的，突然出来一个话题，说出了大家心里想说但不敢说的话，能不火吗？
而且这个话题真的门槛超低！不需要你多专业，也不需要你了解啥背景，是个人就能说两句。
再加上网上那些看热闹不嫌事大的网友，一顿操作下来，热度直接就上去了。

对了，我还看到一些博主也在聊这个话题，不得不说，他们分析得还挺有道理的。

说完了我的观察，来聊聊我自己的感受吧。

我翻了评论，发现大家主要分成几派：
有一派是"完全不理解"党，觉得有啥好讨论的；
还有一派是"代入感超强"党，觉得说的就是自己；
最多的就是"凑热闹"党，管他三七二十一，先评论再说。

我是属于第二派！真的感觉说出了我的心声。
有时候我就在想，为啥网上总有这种话题能引起这么大共鸣？
可能就是因为说出了大家心里话吧。

不过吧，我觉得咱们还是要理性一点。
网上说话不用负责，但咱们自己心里要有数。
别被人带了节奏还不知道是咋回事。

还有就是，别光顾着网上逼逼赖赖，现实生活中该干嘛还得干嘛。
网上说得再热闹，挂了电话还是得上班不是？

{topic}这个话题吧，我觉得还能火一阵子。
毕竟这种话题最容易引发讨论了，而且大家都有表达欲。

姐妹们有啥想法没？你们身边有人聊这个吗？
快来评论区告诉我！我真的好好奇你们都是咋想的！

对了，你们最近还在追啥热点？求推荐！我也需要新素材！

点个赞再走呗~咱们评论区见！

#{topic}
"""
        return article


class AISearcher:
    """AI搜索和观点提取"""

    def __init__(self):
        from config import MINIMAX_API_KEY, MINIMAX_API_BASE
        self.api_key = MINIMAX_API_KEY
        self.api_base = MINIMAX_API_BASE
        import requests

    def search_and_extract(self, keyword: str) -> dict:
        """搜索关键词并提取观点"""
        import requests

        url = f"{self.api_base}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 搜索热点信息
        prompt = f"""关于「{keyword}」这个话题，请帮我：
1. 列出3-5个目前最火的热点/热议点
2. 每个热点用一句话描述

直接输出，格式如下：
热点1: xxx
热点2: xxx
热点3: xxx"""

        payload = {
            "model": "abab6.5s-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            data = response.json()

            highlights = []
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                # 解析热点
                for line in content.split('\n'):
                    if ':' in line or '、' in line:
                        highlights.append(line.strip())

            # 提取观点
            prompt2 = f"""关于「{keyword}」这个话题，请提取3个有价值的观点，用于公众号文章。

要求：
- 每个观点20-40字
- 要能引发读者共鸣或思考
- 观点清晰，有说服力

直接输出观点，用换行分隔"""

            payload2 = {
                "model": "abab6.5s-chat",
                "messages": [{"role": "user", "content": prompt2}],
                "max_tokens": 500
            }

            response2 = requests.post(url, headers=headers, json=payload2, timeout=60)
            data2 = response2.json()

            points = []
            if "choices" in data2 and len(data2["choices"]) > 0:
                content2 = data2["choices"][0]["message"]["content"]
                for line in content2.split('\n'):
                    line = line.strip()
                    if line and len(line) > 5:
                        points.append(line)

            return {
                "highlights": highlights[:5],
                "points": points[:3]
            }

        except Exception as e:
            print(f"搜索失败: {e}")
            return {
                "highlights": [f"{keyword}是近期热门话题"],
                "points": ["这个话题引发了很多人的讨论和关注"]
            }


def generate_from_search(keyword: str, search_result: dict) -> str:
    """根据搜索结果生成风格化文章"""
    import requests
    from config import MINIMAX_API_KEY, MINIMAX_API_BASE

    url = f"{MINIMAX_API_BASE}/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    highlights = search_result.get('highlights', [])
    points = search_result.get('points', [])

    highlights_text = '\n'.join([f"- {h}" for h in highlights])
    points_text = '\n'.join([f"- {p}" for p in points])

    prompt = f"""请帮我写一篇公众号文章

主题：{keyword}

搜索到的热点信息：
{highlights_text}

提取的观点：
{points_text}

要求：
1. 开头：描述这个话题为什么火
2. 中间：结合热点和观点，写3-4段内容
3. 结尾：引导评论互动
4. 风格：亲切自然，像和朋友聊天
5. 字数：800-1200字
6. 直接输出文章内容"""

    payload = {
        "model": "abab6.5s-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"生成失败: {e}")

    # 如果失败，使用模板
    return f"""救命！{keyword}也太火了吧！！

姐妹们！最近{keyword}这个话题你们看到了吗？
我刷微博的时候，简直被刷屏了！
到处都是关于{keyword}的讨论！

说实话，我刚开始还想不就是个话题吗，能有多火？
结果好家伙，点进去一看，好多人在讨论，
而且不同角度的观点都有，看得我瓜都来不及吃...

让我来给你们整理一下目前最火的几个点：

{highlights_text}

---

说实话，我也看了好多观点，最让我有共鸣的是：

{points_text}

---

反正我是被说服了，感觉这个话题真的很有讨论价值。

姐妹们，你们怎么看这个话题？
你们身边有人聊这个吗？
快来评论区告诉我！我真的好好奇！

对了，你们最近还在追啥？求推荐！

点个赞再走呗~咱们评论区见！

#{keyword}
"""


def generate_titles(article_content: str) -> list:
    """生成多个备选标题"""
    return [
        "震惊！这事竟然没人知道",
        "深度好文，关于xx你必须知道的",
        "都在讨论这个，我也来说几句",
    ]
