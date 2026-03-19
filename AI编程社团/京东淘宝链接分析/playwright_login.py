# -*- coding: utf-8 -*-
"""
使用Playwright并指定Chrome用户数据目录来复用已有登录状态
"""
import asyncio
from playwright.async_api import async_playwright
import os
import glob

def find_chrome_user_data_dir():
    """查找Chrome用户数据目录"""
    base_paths = [
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data"),
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data"),
    ]

    for base_path in base_paths:
        if os.path.exists(base_path):
            # 查找Default或其他profile
            profiles = glob.glob(base_path + "\\*")
            for profile in profiles:
                if os.path.isdir(profile):
                    print(f"找到Chrome配置: {profile}")
                    return base_path

    return None

async def main():
    print("查找Chrome用户数据目录...")
    user_data_dir = find_chrome_user_data_dir()

    if not user_data_dir:
        print("未找到Chrome用户数据目录")
        return

    print(f"使用用户数据目录: {user_data_dir}")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=False,
                user_data_dir=user_data_dir
            )

            # 创建新页面并访问商品
            page = await browser.new_page()
            url = "https://detail.tmall.com/item.htm?id=802778589659"
            print(f"打开: {url}")

            await page.goto(url, wait_until="networkidle", timeout=60000)

            # 等待用户操作
            print("\n页面已打开，请手动操作:")
            print("1. 滚动到评价区域")
            print("2. 点击评价/评论标签")
            print("3. 筛选5星评价")
            print("4. 完成后保持浏览器打开")

            # 等待一段时间让用户操作
            await asyncio.sleep(30)

            # 尝试提取评论
            print("\n尝试提取评论...")

            # 保存页面内容
            content = await page.content()
            with open("taobao_page.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("页面已保存到 taobao_page.html")

            # 保持浏览器打开
            print("\n按Ctrl+C结束...")
            await asyncio.Event().wait()

        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
