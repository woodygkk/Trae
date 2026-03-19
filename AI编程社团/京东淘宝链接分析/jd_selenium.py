# -*- coding: utf-8 -*-
"""
使用Selenium连接到京东页面并提取评论
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

ITEM_ID = "10084971961061"

def scrape_jd():
    print("Connecting to Chrome with remote debugging...")

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=options)
        print(f"Connected! Current URL: {driver.current_url}")

        # 检查是否需要登录
        if "passport.jd.com" in driver.current_url or "login.jd.com" in driver.current_url:
            print("Please login first in the browser, then run this script again")
            driver.quit()
            return

        # 如果不在京东商品页面，导航到商品页面
        if str(ITEM_ID) not in driver.current_url:
            url = f"https://item.jd.com/{ITEM_ID}.html"
            print(f"Navigating to: {url}")
            driver.get(url)
            time.sleep(5)

        # 获取页面标题
        title = driver.title
        print(f"\n=== Product Info ===")
        print(f"Title: {title}")

        # 保存页面源码
        with open("jd_product.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page saved to jd_product.html")

        # 滚动到评论区域
        print("\n=== Looking for reviews ===")

        # 尝试找到评论tab并点击
        review_selectors = [
            "//a[contains(text(), '商品评价')]",
            "//a[contains(text(), '评价')]",
            "//div[contains(@class, 'comment')]//a",
            "//li[contains(@data-tab, 'comment')]",
        ]

        for selector in review_selectors:
            try:
                tab = driver.find_element(By.XPATH, selector)
                if tab:
                    print(f"Found review tab: {selector}")
                    tab.click()
                    time.sleep(3)
                    break
            except:
                continue

        # 保存评论页面
        with open("jd_reviews.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Review page saved to jd_reviews.html")

        # 尝试提取评论
        print("\n=== Extracting reviews ===")

        # 查找评论列表
        review_texts = []

        # 尝试多种选择器
        selectors = [
            ".comment-list",
            ".jd.com-list",
            "[class*='comment-list']",
            ".rate-list",
        ]

        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        text = elem.text.strip()
                        if len(text) > 20:
                            review_texts.append(text)
                            print(f"Found review: {text[:100]}...")
            except:
                continue

        # 保存评论
        if review_texts:
            with open("jd_reviews_extracted.txt", "w", encoding="utf-8") as f:
                for i, text in enumerate(review_texts):
                    f.write(f"=== Review {i+1} ===\n")
                    f.write(text + "\n\n")
            print(f"\nSaved {len(review_texts)} reviews to jd_reviews_extracted.txt")
        else:
            print("No reviews extracted automatically")

        print("\nBrowser stays open. Please copy reviews manually or run extraction code.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scrape_jd()
