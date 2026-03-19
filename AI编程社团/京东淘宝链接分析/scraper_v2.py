# -*- coding: utf-8 -*-
"""
淘宝/天猫商品评论爬虫 - 使用Playwright
用于抓取商品的5星评论并分析
"""
import asyncio
import re
from playwright.async_api import async_playwright

ITEM_ID = "802778589659"
ITEM_URL = f"https://detail.tmall.com/item.htm?id={ITEM_ID}"

async def scrape_tmall():
    """使用Playwright抓取天猫商品信息"""
    print(f"开始抓取商品: {ITEM_ID}")
    print("=" * 50)

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 访问商品页面
        print(f"正在打开: {ITEM_URL}")
        await page.goto(ITEM_URL, wait_until="networkidle", timeout=60000)

        # 等待页面加载完成
        await page.wait_for_timeout(3000)

        # 提取商品信息
        product_info = {}

        try:
            # 商品名称 - 通常在title中
            title = await page.title()
            product_info["name"] = title.split('-')[0].strip() if title else "未获取到"
            print(f"商品名称: {product_info['name']}")
        except Exception as e:
            print(f"获取商品名称失败: {e}")
            product_info["name"] = "未获取到"

        try:
            # 价格 - 尝试多种选择器
            price_elem = await page.query_selector('.price .tb-rmb-num')
            if not price_elem:
                price_elem = await page.query_selector('[class*="price"]')
            if price_elem:
                product_info["price"] = await price_elem.inner_text()
            else:
                product_info["price"] = "未获取到"
            print(f"价格: {product_info['price']}")
        except Exception as e:
            print(f"获取价格失败: {e}")
            product_info["price"] = "未获取到"

        try:
            # 店铺名称
            store_elem = await page.query_selector('.shop-name a, .shopName a, [class*="shop"] a')
            if store_elem:
                product_info["store"] = await store_elem.inner_text()
            else:
                product_info["store"] = "未获取到"
            print(f"店铺: {product_info['store']}")
        except Exception as e:
            print(f"获取店铺失败: {e}")
            product_info["store"] = "未获取到"

        # 查找评论tab
        print("\n正在查找评论区域...")

        # 尝试点击评价/评论tab
        review_tab_selectors = [
            'a[href*="#comment"]',
            'a:has-text("评价")',
            'a:has-text("评论")',
            '.tab-has-append:has-text("评价")',
            '[data-tab*="comment"]',
        ]

        for selector in review_tab_selectors:
            try:
                tab = await page.query_selector(selector)
                if tab:
                    await tab.click()
                    print(f"点击了评论tab: {selector}")
                    await page.wait_for_timeout(2000)
                    break
            except:
                continue

        # 滚动页面加载评论
        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(2000)

        # 提取评论内容
        print("\n正在提取评论...")

        # 查找评价文本
        reviews = []
        review_elements = await page.query_selector_all('.rate-list li, .tb-rate-list li, [class*="review"]')

        for i, elem in enumerate(review_elements[:20]):  # 先获取20条
            try:
                text = await elem.inner_text()
                if text and len(text) > 10:  # 过滤太短的评论
                    reviews.append({
                        "text": text.strip(),
                        "index": i + 1
                    })
            except:
                continue

        print(f"提取到 {len(reviews)} 条评论")

        # 保存评论到文件
        with open("reviews_raw.txt", "w", encoding="utf-8") as f:
            for r in reviews:
                f.write(f"=== 评论 {r['index']} ===\n")
                f.write(r["text"] + "\n\n")

        print(f"\n评论已保存到 reviews_raw.txt")
        print(f"共提取 {len(reviews)} 条评论")

        # 保持浏览器打开
        print("\n浏览器保持打开状态...")
        await asyncio.Event().wait()

        await browser.close()

        return product_info, reviews

if __name__ == "__main__":
    asyncio.run(scrape_tmall())
