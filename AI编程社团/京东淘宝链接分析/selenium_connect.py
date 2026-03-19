# -*- coding: utf-8 -*-
"""
使用Selenium连接到已启动的Chrome with remote debugging
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

ITEM_ID = "802778589659"

def scrape_with_selenium():
    print("Connecting to Chrome with remote debugging...")

    # 使用Chrome DevTools Protocol连接到已有浏览器
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=options)
        print(f"Connected! Current URL: {driver.current_url}")

        # 如果不在商品页面，则导航到商品页面
        if "tmall.com" not in driver.current_url and "taobao.com" not in driver.current_url:
            url = f"https://detail.tmall.com/item.htm?id={ITEM_ID}"
            print(f"Navigating to: {url}")
            driver.get(url)
            time.sleep(5)

        print("\n=== Product Info ===")
        try:
            title = driver.title
            print(f"Title: {title}")
        except:
            pass

        # 保存页面源码
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html")

        # 尝试查找评论tab
        print("\n=== Looking for review section ===")

        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 查找评价相关的元素
        review_keywords = ["评价", "评论", "累计评论", "心得"]

        for keyword in review_keywords:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                if elements:
                    print(f"Found '{keyword}': {len(elements)} elements")
                    for elem in elements[:3]:
                        try:
                            print(f"  - {elem.tag_name}: {elem.text[:50]}")
                        except:
                            pass
            except Exception as e:
                pass

        # 尝试点击评价tab
        print("\n=== Trying to click review tab ===")
        try:
            # 尝试多种选择器
            tab_selectors = [
                "//a[contains(text(), '评价')]",
                "//a[contains(text(), '评论')]",
                "//div[contains(@class, 'rate')]//a",
            ]

            for selector in tab_selectors:
                try:
                    tab = driver.find_element(By.XPATH, selector)
                    if tab:
                        print(f"Clicking: {selector}")
                        tab.click()
                        time.sleep(3)
                        break
                except:
                    continue
        except Exception as e:
            print(f"Click error: {e}")

        # 保存评论页面的源码
        with open("review_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Review page saved to review_page.html")

        # 保持浏览器打开
        print("\nBrowser stays open. Please manually:")
        print("1. Click on review/evaluation tab")
        print("2. Filter by 5 stars")
        print("3. Scroll to load reviews")
        print("4. Copy review text when done")

        input("\nPress Enter to close browser...")

        driver.quit()

    except Exception as e:
        print(f"Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scrape_with_selenium()
