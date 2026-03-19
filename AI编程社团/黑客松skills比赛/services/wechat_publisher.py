# -*- coding: utf-8 -*-
"""
公众号发布服务
通过浏览器自动化将文章发布到公众号草稿箱
"""

import time
import os


class WeChatPublisher:
    """微信公众号发布器"""

    def __init__(self):
        self.driver = None

    def publish_to_draft(self, title: str, content: str) -> bool:
        """
        发布文章到公众号草稿箱

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            是否发布成功
        """
        print("正在打开微信公众号后台...")
        print("注意：需要你扫码登录微信公众号")

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            from webdriver_manager.chrome import ChromeDriverManager
            import pyperclip

            # 先把内容复制到剪贴板
            full_content = f"{title}\n\n{content}"
            pyperclip.copy(full_content)

            # 设置Chrome选项
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # 初始化浏览器
            print("正在启动浏览器...")
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            # 去除webdriver标识
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            # 打开微信公众号后台
            print("正在打开微信公众号后台...")
            self.driver.get("https://mp.weixin.qq.com/")

            # 等待用户扫码登录
            print("\n" + "=" * 50)
            print("请在浏览器中扫码登录微信公众号")
            print("登录成功后，程序会自动继续")
            print("=" * 50 + "\n")

            # 等待用户登录
            WebDriverWait(self.driver, 300).until(
                EC.url_contains("cgi-bin/home")
            )

            print("登录成功！")

            # 直接跳转新建图文页面
            print("正在打开新建图文消息页面...")
            self.driver.get("https://mp.weixin.qq.com/cgi/appmsg?t=media/appmsg_edit_v2")
            time.sleep(5)

            # 尝试粘贴内容
            print("正在粘贴内容...")
            try:
                # 尝试 Ctrl+V 粘贴
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.CONTROL, 'v')
                print("已发送 Ctrl+V")
                time.sleep(2)
            except Exception as e:
                print(f"自动粘贴失败: {e}")

            print("\n" + "=" * 50)
            print("[OK] 已打开公众号编辑页面")
            print("内容已复制到剪贴板，请手动：")
            print("1. 在标题栏填入标题")
            print("2. 在内容区 Ctrl+V 粘贴内容")
            print("3. 点击[保存到草稿箱]")
            print("=" * 50)
            print("\n操作完成后，按回车键关闭浏览器...")

            input()
            self.driver.quit()
            return True

        except ImportError:
            print("\n" + "=" * 50)
            print("请先安装 selenium 和 webdriver_manager:")
            print("pip install selenium webdriver-manager")
            print("=" * 50)
            return False
        except Exception as e:
            print(f"发布失败: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return False


def publish_article(title: str, content: str) -> bool:
    """快捷发布函数"""
    publisher = WeChatPublisher()
    return publisher.publish_to_draft(title, content)


if __name__ == "__main__":
    # 测试
    publish_article("测试标题", "测试内容")
