# -*- coding: utf-8 -*-
"""
配置文件
在这里配置你的API密钥和各种参数
"""

# ============== AI API 配置 ==============
# 选择你要使用的AI服务: "openai", "claude" 或 "minimax"
AI_PROVIDER = "minimax2.5"

# OpenAI API 配置
# 替换成你自己的API Key
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Claude API 配置
# 替换成你自己的API Key
CLAUDE_API_KEY = "sk-ant-your-claude-api-key-here"

# MiniMax API 配置
# 替换成你自己的API Key
MINIMAX_API_KEY = "sk-cp-WsBzZ5kPtrd7LD6PXiutSDpk_hNGLGbtgYeKsjRVLuiC0QhH9ZnY41nAWI77657RlD7ehCwMsVM2g-EsPSzqY2Usg6fhJnwcKHXjfKsvpdHgRbfGU3OSdcY"
# MiniMax API地址（根据你的API类型选择）
MINIMAX_API_BASE = "https://api.minimax.chat/v1"

# ============== 爬虫配置 ==============
# 请求间隔（秒），不要设太短否则容易被封IP
REQUEST_DELAY = 2

# 每次获取热点数量
HOT_TOPIC_LIMIT = 10

# ============== 文章配置 ==============
# 生成文章的字数（大约）
ARTICLE_WORD_COUNT = 2000

# 你的写作风格描述（AI会用这个来模仿你的风格）
WRITING_STYLE = """
你是一个小红书风格的博主，
语言风格：亲切、自然、有趣
文章结构：开头抓住眼球、中间干货满满、结尾引发互动
"""
