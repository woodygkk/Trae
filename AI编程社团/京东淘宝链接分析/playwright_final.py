# -*- coding: utf-8 -*-
"""
使用Playwright的persistent_context来复用Chrome登录状态
"""
import asyncio
from playwright.async_api import async_playwright
import os
import time

USER_DATA_DIR = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"

async def main():
    print(f"Using Chrome user data: {USER_DATA_DIR}")

    async with async_playwright() as p:
        try:
            # 使用 launch_persistent_context
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False,
                viewport={"width": 1280, "height": 720}
            )

            # 创建新页面并访问商品
            page = await context.new_page()
            url = "https://detail.tmall.com/item.htm?id=802778589659"
            print(f"Opening: {url}")

            await page.goto(url, wait_until="networkidle", timeout=60000)

            print("\nPage loaded. Please:")
            print("1. Click on 'Evaluation' or 'Review' tab")
            print("2. Filter by 5 stars")
            print("3. Scroll to load more reviews")
            print("4. When done, say 'done' or 'OK'")

            # 等待用户操作
            print("\nWaiting for 60 seconds...")
            await asyncio.sleep(60)

            # 尝试提取评论
            print("\nTrying to extract reviews...")

            # 尝试多种选择器来获取评论
            review_texts = []

            # 天猫评论选择器
            selectors = [
                ".rate-list",
                ".tb-rate-list",
                "[class*='rate-list']",
                ".rate-detail",
                "#J-RateReviews",
            ]

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"Found selector: {selector}, elements: {len(elements)}")
                        for elem in elements[:5]:
                            text = await elem.inner_text()
                            if text and len(text) > 20:
                                review_texts.append(text)
                except Exception as e:
                    pass

            # 保存页面内容
            content = await page.content()
            with open("taobao_page.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Page saved to taobao_page.html")

            # 保存评论
            if review_texts:
                with open("reviews_extracted.txt", "w", encoding="utf-8") as f:
                    for i, text in enumerate(review_texts):
                        f.write(f"=== Review {i+1} ===\n")
                        f.write(text[:500] + "\n\n")
                print(f"Saved {len(review_texts)} reviews to reviews_extracted.txt")
            else:
                print("No reviews extracted, please copy manually")

            # 保持浏览器打开
            print("\nBrowser stays open. Say 'done' when ready...")
            await asyncio.Event().wait()

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
