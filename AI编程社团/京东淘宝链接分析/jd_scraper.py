# -*- coding: utf-8 -*-
"""
京东商品评论爬虫 - 使用移动端API
"""
import requests
import json
import re

ITEM_ID = "10084971961061"

# 京东移动端API
def get_jd_reviews():
    """通过京东移动端API获取评论"""
    print(f"Fetching JD reviews for item: {ITEM_ID}")

    # 尝试京东移动端评论API
    api_url = "https://api.m.jd.com/client.action"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0",
        "Referer": "https://m.jd.com/",
        "Accept": "*/*",
    }

    # 获取评论列表
    params = {
        "functionId": "queryCommentList",
        "body": json.dumps({
            "skuId": ITEM_ID,
            "page": 1,
            "pageSize": 20,
            "score": 5,  # 5星评论
            "sortType": 5,
            "isThread": 1
        }),
        "appid": "m-jd-home",
        "client": "m-jd-home",
        "clientVersion": "3.9.0"
    }

    try:
        print("Trying JD API...")
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])

    except Exception as e:
        print(f"API Error: {e}")

    # 尝试H5接口
    print("\n\nTrying H5 API...")
    h5_url = f"https://item.m.jd.com/product/{ITEM_ID}.html"
    try:
        response = requests.get(h5_url, headers=headers, timeout=10)
        print(f"H5 Status: {response.status_code}")
        print(response.text[:500])
    except Exception as e:
        print(f"H5 Error: {e}")

if __name__ == "__main__":
    get_jd_reviews()
