# -*- coding: utf-8 -*-
"""
使用Selenium连接已打开的浏览器抓取淘宝评论
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

ITEM_ID = "802778589659"

def scrape_with_selenium():
    print("尝试使用Selenium抓取...")

    # 使用Chrome DevTools Protocol连接到已有浏览器
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=options)
        print(f"已连接到浏览器，当前URL: {driver.current_url}")

        # 检查是否是天猫商品页面
        if "tmall.com" in driver.current_url or "taobao.com" in driver.current_url:
            print("已连接到淘宝/天猫页面")

            # 提取商品名称
            try:
                title = driver.title
                print(f"页面标题: {title}")
            except:
                print("无法获取标题")

            # 提取页面源码保存
            page_source = driver.page_source
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("页面源码已保存到 page_source.html")

            # 尝试查找评论元素
            print("\n尝试查找评论元素...")

            # 查找评价相关的链接/按钮
            selectors = [
                "//a[contains(text(), '评价')]",
                "//a[contains(text(), '评论')]",
                "//div[contains(@class, 'rate')]",
                "//ul[contains(@class, 'rate')]",
            ]

            for selector in selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"找到 {len(elements)} 个元素: {selector}")
                        for i, elem in enumerate(elements[:3]):
                            try:
                                text = elem.text[:200]
                                print(f"  元素 {i}: {text[:100]}...")
                            except:
                                pass
                except Exception as e:
                    print(f"  查询失败: {e}")

        else:
            print(f"当前不在淘宝/天猫页面: {driver.current_url}")

    except Exception as e:
        print(f"连接失败: {e}")
        print("\n请确保Chrome以调试模式运行:")
        print('  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')

if __name__ == "__main__":
    scrape_with_selenium()
