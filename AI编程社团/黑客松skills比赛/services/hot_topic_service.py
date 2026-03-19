# -*- coding: utf-8 -*-
"""
热点服务
整合所有平台的热点数据
"""

from typing import List, Dict
from spiders import WeiboSpider, ZhihuSpider, DouyinSpider
from config import HOT_TOPIC_LIMIT


class HotTopicService:
    """热点话题服务"""

    def __init__(self):
        self.weibo_spider = WeiboSpider()
        self.zhihu_spider = ZhihuSpider()
        self.douyin_spider = DouyinSpider()

    def get_all_topics(self, platforms: List[str] = None) -> List[Dict]:
        """
        获取所有平台的热点话题

        Args:
            platforms: 要获取的平台列表，如 ["微博", "知乎", "抖音"]
                     如果为 None，则获取所有平台

        Returns:
            整合后的热点话题列表，按热度排序
        """
        all_topics = []

        # 微博
        if not platforms or "微博" in platforms:
            weibo_topics = self.weibo_spider.get_hot_search(HOT_TOPIC_LIMIT)
            all_topics.extend(weibo_topics)

        # 知乎
        if not platforms or "知乎" in platforms:
            zhihu_topics = self.zhihu_spider.get_hot_search(HOT_TOPIC_LIMIT)
            all_topics.extend(zhihu_topics)

        # 抖音
        if not platforms or "抖音" in platforms:
            douyin_topics = self.douyin_spider.get_hot_search(HOT_TOPIC_LIMIT)
            all_topics.extend(douyin_topics)

        # 按热度排序
        all_topics.sort(key=lambda x: x.get("hot_score", 0), reverse=True)

        return all_topics

    def select_platform_topics(self, platform: str) -> List[Dict]:
        """获取指定平台的热点"""
        if platform == "微博":
            return self.weibo_spider.get_hot_search(HOT_TOPIC_LIMIT)
        elif platform == "知乎":
            return self.zhihu_spider.get_hot_search(HOT_TOPIC_LIMIT)
        elif platform == "抖音":
            return self.douyin_spider.get_hot_search(HOT_TOPIC_LIMIT)
        else:
            return []


if __name__ == "__main__":
    # 测试
    service = HotTopicService()
    topics = service.get_all_topics()
    print("\n=== 热门话题排行榜 ===")
    for i, topic in enumerate(topics[:10], 1):
        print(f"{i}. [{topic['platform']}] {topic['title']} (热度: {topic['hot_score']})")
