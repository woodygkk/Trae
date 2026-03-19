# -*- coding: utf-8 -*-
"""
微博热搜爬虫
抓取微博热搜榜单上的热门话题
"""

import requests
import time
from typing import List, Dict
from config import REQUEST_DELAY


class WeiboSpider:
    """微博热搜爬虫"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://weibo.com",
        }
        self.api_url = "https://weibo.com/ajax/side/hotSearch"

    def get_hot_search(self, limit: int = 10) -> List[Dict]:
        """
        获取微博热搜列表

        Args:
            limit: 返回数量限制

        Returns:
            热搜话题列表，每条包含 title, hot_score, url
        """
        try:
            print("正在获取微博热搜...")
            time.sleep(REQUEST_DELAY)

            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            data = response.json()

            if data.get("ok") != 1:
                print(f"获取微博热搜失败: {data}")
                return []

            items = data.get("data", {}).get("realtime", [])
            topics = []

            for item in items[:limit]:
                topic = {
                    "title": item.get("word", ""),
                    "hot_score": item.get("num", 0),
                    "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                    "platform": "微博"
                }
                topics.append(topic)

            print(f"获取到 {len(topics)} 条微博热搜")
            return topics

        except Exception as e:
            print(f"获取微博热搜出错: {e}")
            return []


if __name__ == "__main__":
    # 测试
    spider = WeiboSpider()
    results = spider.get_hot_search(5)
    for i, topic in enumerate(results, 1):
        print(f"{i}. {topic['title']} (热度: {topic['hot_score']})")
