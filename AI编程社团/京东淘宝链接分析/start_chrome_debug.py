# -*- coding: utf-8 -*-
"""
启动Chrome并启用远程调试
然后使用Selenium连接
"""
import subprocess
import time
import os

# 先检查是否有Chrome在运行
print("Checking for existing Chrome with remote debugging...")

# 启动Chrome with remote debugging
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
remote_debug_args = [
    chrome_path,
    "--remote-debugging-port=9222",
    "--no-first-run",
    "--no-default-browser-check",
    "--user-data-dir=C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\TempProfile"
]

print(f"Launching Chrome with remote debugging...")
print(" ".join(remote_debug_args))

# 启动Chrome进程
proc = subprocess.Popen(remote_debug_args)
print(f"Chrome launched with PID: {proc.pid}")

# 等待Chrome启动
time.sleep(5)

print("\nNow we can connect with Selenium using:")
print("options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')")
