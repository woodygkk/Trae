# -*- coding: utf-8 -*-
"""
使用Selenium连接到京东页面并提取评论 - 自动版本
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

ITEM_ID = "10084971961061"

print("Starting JD scraper...")

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=options)
    print(f"Current URL: {driver.current_url}")

    # 导航到京东商品页面
    url = f"https://item.jd.com/{ITEM_ID}.html"
    print(f"Navigating to: {url}")
    driver.get(url)
    time.sleep(5)

    # 获取标题
    title = driver.title
    print(f"Title: {title}")

    # 保存页面
    with open("jd_product.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved jd_product.html")

    # 点击评价tab
    try:
        tabs = driver.find_elements(By.XPATH, "//a[contains(text(), '评价')]")
        for tab in tabs:
            if tab.is_displayed():
                print(f"Clicking: {tab.text}")
                tab.click()
                time.sleep(3)
                break
    except Exception as e:
        print(f"Click error: {e}")

    # 保存评论页
    with open("jd_reviews.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved jd_reviews.html")

    # 尝试提取评论文本
    reviews = []
    try:
        # 尝试多种选择器
        selectors = [
            "//p[@class='comment-con']",
            "//div[@class='comment-item']",
            "//div[contains(@class, 'comment')]",
        ]

        for sel in selectors:
            items = driver.find_elements(By.XPATH, sel)
            print(f"Selector {sel}: found {len(items)}")
            for item in items[:10]:
                text = item.text.strip()
                if len(text) > 10:
                    reviews.append(text)
                    print(f"Review: {text[:50]}...")
    except Exception as e:
        print(f"Extract error: {e}")

    if reviews:
        with open("jd_reviews.txt", "w", encoding="utf-8") as f:
            for i, r in enumerate(reviews):
                f.write(f"=== {i+1} ===\n{r}\n\n")
        print(f"Saved {len(reviews)} reviews")
    else:
        print("No reviews found")

    print("Done!")

except Exception as e:
    print(f"Error: {e}")

print("Script finished")
