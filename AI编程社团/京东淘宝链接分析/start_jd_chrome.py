# -*- coding: utf-8 -*-
import subprocess
import time
import os

# Kill existing Chrome with remote debugging
os.system('taskkill /F /IM chrome.exe 2>nul')

# Start Chrome with remote debugging
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
args = [
    chrome_path,
    "--remote-debugging-port=9222",
    "--no-first-run",
    "--user-data-dir=C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\DebugProfile"
]

print("Starting Chrome...")
subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Chrome started")
