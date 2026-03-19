# -*- coding: utf-8 -*-
import sys
import threading
import time

def run_script():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        print("Creating driver...", flush=True)

        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        print("Connecting...", flush=True)
        driver = webdriver.Chrome(options=options)

        print(f"Connected! URL: {driver.current_url}", flush=True)

        # Navigate to JD
        driver.get("https://item.jd.com/10084971961061.html")
        print(f"Navigated: {driver.current_url}", flush=True)

        title = driver.title
        print(f"Title: {title}", flush=True)

        # Save page
        with open("jd_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved jd_page.html", flush=True)

        driver.quit()
        print("DONE!", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

# Run with timeout
result = []
def target():
    result.append("done")

t = threading.Thread(target=run_script)
t.daemon = True
t.start()
t.join(timeout=30)

if t.is_alive():
    print("TIMEOUT - script took too long", flush=True)
    sys.exit(1)
