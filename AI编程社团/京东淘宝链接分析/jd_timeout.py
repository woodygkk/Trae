# -*- coding: utf-8 -*-
import sys
import signal

def timeout_handler(signum, frame):
    print("Timeout!", flush=True)
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

print("Starting JD scraper...", flush=True)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    print("Imports done", flush=True)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    print("Options set", flush=True)

    print("Creating driver...", flush=True)
    driver = webdriver.Chrome(options=options)
    print(f"Connected! URL: {driver.current_url}", flush=True)

    # Navigate to JD product
    driver.get("https://item.jd.com/10084971961061.html")
    print(f"Navigated to: {driver.current_url}", flush=True)

    # Get title
    title = driver.title
    print(f"Title: {title}", flush=True)

    # Save page
    with open("jd_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved jd_page.html", flush=True)

    signal.alarm(0)  # Cancel timeout
    print("SUCCESS!", flush=True)

except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
