# -*- coding: utf-8 -*-
"""
淘宝/天猫商品评论爬虫
用于抓取商品的5星评论并分析
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

# 配置
ITEM_ID = "802778589659"
BASE_URL = f"https://detail.tmall.com/item.htm?id={ITEM_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def get_product_info():
    """获取商品基本信息"""
    print("正在获取商品信息...")
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取商品名称
        product_name = soup.find('title')
        product_name = product_name.text if product_name else "未获取到"

        # 尝试从页面提取价格
        price = "未获取到"
        price_elem = soup.find('span', class_=re.compile('price'))
        if price_elem:
            price = price_elem.text

        # 尝试提取店铺名称
        store_name = "未获取到"
        store_elem = soup.find('a', class_=re.compile('shop'))
        if store_elem:
            store_name = store_elem.text.strip()

        # 提取评论数量
        review_count = "未获取到"
        review_elem = soup.find('span', class_=re.compile('count'))
        if review_elem:
            review_count = review_elem.text

        print(f"商品名称: {product_name}")
        print(f"价格: {price}")
        print(f"店铺: {store_name}")
        print(f"评论数: {review_count}")

        return {
            "name": product_name,
            "price": price,
            "store": store_name,
            "review_count": review_count
        }
    except Exception as e:
        print(f"获取商品信息失败: {e}")
        return None

def get_reviews():
    """获取商品评论"""
    print("\n正在获取评论...")

    # 淘宝/天猫评论API
    reviews_api = f"https://rate.tmall.com/list_detail_rate.htm?itemId={ITEM_ID}&sellerId=0&currentPage=1"

    try:
        response = requests.get(reviews_api, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'

        # 解析返回的JSONP格式
        content = response.text
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            print("评论API返回数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
        else:
            print("评论内容:")
            print(content[:500])

    except Exception as e:
        print(f"获取评论失败: {e}")

if __name__ == "__main__":
    print(f"开始分析商品: {ITEM_ID}")
    print("=" * 50)

    # 获取商品信息
    product_info = get_product_info()

    # 获取评论
    get_reviews()
