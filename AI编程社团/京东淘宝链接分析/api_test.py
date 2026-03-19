# -*- coding: utf-8 -*-
"""
尝试通过移动端API获取淘宝评论
"""
import requests
import json
import re

ITEM_ID = "802778589659"

# 淘宝移动端API
API_URL = f"https://h5api.m.taobao.com/h5/mtop.taobao.rate.detaillist.get/6.0/"

params = {
    "data": json.dumps({
        "itemId": ITEM_ID,
        "sellerId": "0",
        "currentPage": "1",
        "pageSize": "20"
    })
}

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0",
    "Referer": "https://m.taobao.com/",
    "Accept": "application/json"
}

print("尝试通过移动端API获取评论...")
print(f"API: {API_URL}")
print(f"Params: {params}")

try:
    response = requests.get(API_URL, params=params, headers=headers, timeout=10)
    print(f"\n响应状态: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
except Exception as e:
    print(f"请求失败: {e}")

# 尝试京东API
print("\n\n尝试京东API...")
jd_api = f"https://api.m.jd.com/client.action?functionId=queryCommentDetail&body={{\"skuId\":\"{ITEM_ID}\",\"page\":1,\"pageSize\":20}}"

jd_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://item.jd.com/"
}

try:
    jd_response = requests.get(jd_api, headers=jd_headers, timeout=10)
    print(f"京东响应: {jd_response.text[:300]}")
except Exception as e:
    print(f"京东请求失败: {e}")
