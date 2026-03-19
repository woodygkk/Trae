# -*- coding: utf-8 -*-
"""
知乎热榜爬虫
抓取知乎热榜上的热门问题
"""

import requests
import time
from typing import List, Dict
from config import REQUEST_DELAY


class ZhihuSpider:
    """知乎热榜爬虫"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.zhihu.com",
        }
        self.api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total=50?limit&desktop=true"

    def get_hot_search(self, limit: int = 10) -> List[Dict]:
        """
        获取知乎热榜列表

        Args:
            limit: 返回数量限制

        Returns:
            热榜问题列表，每条包含 title, hot_score, url
        """
        try:
            print("正在获取知乎热榜...")
            time.sleep(REQUEST_DELAY)

            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            data = response.json()

            items = data.get("data", [])
            topics = []

            for item in items[:limit]:
                topic = {
                    "title": item.get("target", {}).get("title", ""),
                    "hot_score": item.get("detail_text", ""),
                    "url": f"https://www.zhihu.com/question/{item.get('target', {}).get('id', '')}",
                    "platform": "知乎"
                }
                topics.append(topic)

            print(f"获取到 {len(topics)} 条知乎热榜")
            return topics

        except Exception as e:
            print(f"获取知乎热榜出错: {e}")
            return []


if __name__ == "__main__":
    # 测试
    spider = ZhihuSpider()
    results = spider.get_hot_search(5)
    for i, topic in enumerate(results, 1):
        print(f"{i}. {topic['title']} ({topic['hot_score']})")
