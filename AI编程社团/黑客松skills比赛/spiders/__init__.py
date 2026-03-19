# -*- coding: utf-8 -*-
"""
爬虫模块
"""

from .weibo_spider import WeiboSpider
from .zhihu_spider import ZhihuSpider
from .douyin_spider import DouyinSpider

__all__ = ["WeiboSpider", "ZhihuSpider", "DouyinSpider"]
