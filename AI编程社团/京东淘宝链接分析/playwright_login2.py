# -*- coding: utf-8 -*-
"""
使用Playwright的persistent_context来复用Chrome登录状态
"""
import asyncio
from playwright.async_api import async_playwright
import os

USER_DATA_DIR = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"

async def main():
    print(f"使用Chrome用户数据: {USER_DATA_DIR}")

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
            print(f"打开: {url}")

            await page.goto(url, wait_until="networkidle", timeout=60000)

            print("\n页面已加载，请手动操作:")
            print("1. 点击'评价'或'评论'标签")
            print("2. 筛选5星评价")
            print("3. 滚动加载更多评论")
            print("4. 完成后回复'已准备好评论'")

            # 保持浏览器打开
            print("\n等待操作完成...")
            await asyncio.Event().wait()

        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
