#!/usr/bin/env python3
"""
Push Notification Module
Supports multiple platforms: Feishu, WeChatWork, DingTalk, Telegram, Email
"""

import requests
import json
import logging
import os
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)


def format_for_markdown(articles, count=10):
    """
    Format articles as Markdown for messaging platforms

    Args:
        articles (list): List of article dictionaries
        count (int): Number of articles to include

    Returns:
        str: Formatted markdown text
    """
    content = f"# 🤖 AI Today's Top News\n\n"
    content += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"**Articles**: {min(count, len(articles))}\n\n"
    content += "---\n\n"

    for i, article in enumerate(articles[:count], 1):
        emoji = "🔥" if i <= 3 else "📰"

        content += f"## {emoji} Top {i}: {article['title']}\n\n"
        content += f"**Source**: {article['source']} | "
        content += f"**Category**: {article['category']} | "
        content += f"**Score**: {article['score']:.1f}\n\n"

        # Time ago
        published = article['published']
        if published.tzinfo is not None:
            published = published.replace(tzinfo=None)
        age_hours = (datetime.now() - published).total_seconds() / 3600
        if age_hours < 1:
            time_str = f"{int(age_hours * 60)} min ago"
        elif age_hours < 24:
            time_str = f"{int(age_hours)} hours ago"
        else:
            time_str = f"{int(age_hours / 24)} days ago"

        content += f"**Published**: {time_str}\n\n"

        # Summary (truncated)
        summary = article.get('summary', '')
        if len(summary) > 150:
            summary = summary[:150] + "..."

        content += f"{summary}\n\n"
        content += f"[Read More]({article['link']})\n\n"
        content += "---\n\n"

    return content


def send_to_feishu(webhook_url, content):
    """
    Send message to Feishu (Lark) group bot

    Args:
        webhook_url (str): Feishu webhook URL
        content (str): Markdown content

    Returns:
        dict: API response
    """
    try:
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🤖 AI Today's Top News"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        result = response.json()

        if result.get('code') == 0:
            logger.info("Successfully sent to Feishu")
        else:
            logger.error(f"Feishu error: {result}")

        return result

    except Exception as e:
        logger.error(f"Feishu push failed: {e}")
        return {"error": str(e)}


def send_to_wechat_work(webhook_url, content):
    """
    Send message to WeChatWork (企业微信) group bot

    Args:
        webhook_url (str): WeChatWork webhook URL
        content (str): Markdown content

    Returns:
        dict: API response
    """
    try:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        result = response.json()

        if result.get('errcode') == 0:
            logger.info("Successfully sent to WeChatWork")
        else:
            logger.error(f"WeChatWork error: {result}")

        return result

    except Exception as e:
        logger.error(f"WeChatWork push failed: {e}")
        return {"error": str(e)}


def send_to_dingtalk(webhook_url, content, secret=None):
    """
    Send message to DingTalk (钉钉) group bot

    Args:
        webhook_url (str): DingTalk webhook URL
        content (str): Markdown content
        secret (str): Optional security secret

    Returns:
        dict: API response
    """
    try:
        import time
        import hmac
        import hashlib
        import base64
        import urllib.parse

        # Add signature if secret provided
        url = webhook_url
        if secret:
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = f'{timestamp}\n{secret}'
            string_to_sign_enc = string_to_sign.encode('utf-8')

            hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                               digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

            url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI Today's Top News",
                "text": content
            }
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get('errcode') == 0:
            logger.info("Successfully sent to DingTalk")
        else:
            logger.error(f"DingTalk error: {result}")

        return result

    except Exception as e:
        logger.error(f"DingTalk push failed: {e}")
        return {"error": str(e)}


def send_to_telegram(bot_token, chat_id, content):
    """
    Send message to Telegram

    Args:
        bot_token (str): Telegram bot token
        chat_id (str): Telegram chat ID
        content (str): Markdown content

    Returns:
        dict: API response
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Telegram has message length limit
        if len(content) > 4096:
            content = content[:4090] + "..."

        payload = {
            "chat_id": chat_id,
            "text": content,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get('ok'):
            logger.info("Successfully sent to Telegram")
        else:
            logger.error(f"Telegram error: {result}")

        return result

    except Exception as e:
        logger.error(f"Telegram push failed: {e}")
        return {"error": str(e)}


def send_email(to_email, subject, content):
    """
    Send email using capymail CLI

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        content (str): Email body (markdown)

    Returns:
        dict: Send result
    """
    try:
        # Check if send-email command exists
        result = subprocess.run(['which', 'send-email'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning("send-email command not found, skipping email")
            return {"error": "send-email not available"}

        # Send email using send-email CLI
        cmd = [
            'send-email',
            '--to', to_email,
            '--subject', subject,
            '--body', content
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            logger.info(f"Successfully sent email to {to_email}")
            return {"status": "success", "output": result.stdout}
        else:
            logger.error(f"Email send failed: {result.stderr}")
            return {"error": result.stderr}

    except Exception as e:
        logger.error(f"Email push failed: {e}")
        return {"error": str(e)}


def push_to_channels(articles, config, count=10):
    """
    Push articles to all configured channels

    Args:
        articles (list): List of article dictionaries
        config (dict): Push configuration
        count (int): Number of articles to push

    Returns:
        list: List of (channel, result) tuples
    """
    content = format_for_markdown(articles, count)
    results = []

    # Feishu
    if config.get('feishu', {}).get('enabled'):
        webhook = config['feishu'].get('webhook')
        if webhook:
            result = send_to_feishu(webhook, content)
            results.append(('Feishu', result))

    # WeChatWork
    if config.get('wechat_work', {}).get('enabled'):
        webhook = config['wechat_work'].get('webhook')
        if webhook:
            result = send_to_wechat_work(webhook, content)
            results.append(('WeChatWork', result))

    # DingTalk
    if config.get('dingtalk', {}).get('enabled'):
        webhook = config['dingtalk'].get('webhook')
        secret = config['dingtalk'].get('secret')
        if webhook:
            result = send_to_dingtalk(webhook, content, secret)
            results.append(('DingTalk', result))

    # Telegram
    if config.get('telegram', {}).get('enabled'):
        bot_token = config['telegram'].get('bot_token')
        chat_id = config['telegram'].get('chat_id')
        if bot_token and chat_id:
            result = send_to_telegram(bot_token, chat_id, content)
            results.append(('Telegram', result))

    # Email
    if config.get('email', {}).get('enabled'):
        to_email = config['email'].get('to')
        if to_email:
            subject = f"AI Today's Top News - {datetime.now().strftime('%Y-%m-%d')}"
            result = send_email(to_email, subject, content)
            results.append(('Email', result))

    return results


if __name__ == '__main__':
    # Test push
    logging.basicConfig(level=logging.INFO)

    test_articles = [
        {
            'title': 'OpenAI Releases GPT-5',
            'link': 'https://example.com',
            'published': datetime.now(),
            'summary': 'OpenAI announces GPT-5 with breakthrough capabilities...',
            'source': 'OpenAI Blog',
            'category': '产品发布',
            'score': 95.5
        }
    ]

    content = format_for_markdown(test_articles)
    print(content)
