# -*- coding: utf-8 -*-
import sys
print("Starting...", flush=True)

try:
    from selenium import webdriver
    print("Selenium imported", flush=True)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    print("Connecting...", flush=True)

    driver = webdriver.Chrome(options=options)
    print(f"URL: {driver.current_url}", flush=True)

    driver.get("https://item.jd.com/10084971961061.html")
    print(f"After nav: {driver.current_url}", flush=True)

    with open("jd_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved jd_page.html", flush=True)

    driver.quit()
    print("Done", flush=True)

except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
