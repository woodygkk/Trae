#!/usr/bin/env python3
"""
Twitter/X Scraping Module
Scrapes tweets from Twitter/X using Playwright
"""

import hashlib
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# Twitter accounts to scrape (high-value AI accounts)
TWITTER_ACCOUNTS = [
    {'username': 'OpenAI', 'name': 'OpenAI', 'authority_score': 30},
    {'username': 'AnthropicAI', 'name': 'AnthropicAI', 'authority_score': 30},
    {'username': 'GoogleAI', 'name': 'GoogleAI', 'authority_score': 30},
    {'username': 'GoogleDeepMind', 'name': 'GoogleDeepMind', 'authority_score': 30},
    {'username': 'ylecun', 'name': 'Yann LeCun', 'authority_score': 28},
    {'username': 'AndrewYNg', 'name': 'Andrew Ng', 'authority_score': 28},
    {'username': 'kaboretweet', 'name': 'Kaboretweet', 'authority_score': 25},
    {'username': 'DrJimFan', 'name': 'Jim Fan', 'authority_score': 26},
    {'username': 'sama', 'name': 'Sam Altman', 'authority_score': 30},
    {'username': 'tsaborowicz', 'name': 'Thomas Saborowicz', 'authority_score': 22},
]


def get_browser():
    """Get Playwright browser instance"""
    try:
        from playwright.sync_api import sync_playwright
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        return browser, playwright
    except ImportError:
        logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return None, None
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        return None, None


def parse_tweet_date(date_str):
    """Parse Twitter date format to datetime"""
    try:
        # Twitter format: "12:30 PM · Mar 17, 2026"
        from dateutil import parser
        return parser.parse(date_str)
    except:
        return datetime.now()


def scrape_twitter_user(username, authority_score, max_tweets=20):
    """
    Scrape tweets from a single Twitter user

    Args:
        username: Twitter username (without @)
        authority_score: Authority score for this source
        max_tweets: Maximum number of tweets to fetch

    Returns:
        list: List of tweet articles
    """
    browser, playwright = get_browser()
    if not browser:
        return []

    articles = []
    try:
        context = browser.contexts[0]
        page = context.new_page()

        # Construct the URL - Twitter now uses /with_replies for full timeline
        url = f"https://twitter.com/{username}"

        logger.info(f"Scraping Twitter: @{username}")

        # Set extra HTTP headers to mimic real browser
        page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        page.goto(url, wait_until='domcontentloaded', timeout=30000)

        # Wait for tweets to load
        page.wait_for_selector('article', timeout=10000)

        # Scroll to load more tweets
        for _ in range(3):
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)

        # Extract tweets
        tweets = page.query_selector_all('article')

        for tweet in tweets[:max_tweets]:
            try:
                # Get tweet text
                text_elem = tweet.query_selector('div[data-testid="tweetText"]')
                if not text_elem:
                    continue
                title = text_elem.inner_text()[:200]  # Limit title length

                # Get tweet link
                link_elem = tweet.query_selector('a[href*="/status/"]')
                if not link_elem:
                    continue
                link = link_elem.get_attribute('href')
                if not link.startswith('http'):
                    link = f"https://twitter.com{link}"

                # Get timestamp
                time_elem = tweet.query_selector('time')
                if time_elem:
                    datetime_str = time_elem.get_attribute('datetime')
                    try:
                        published = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    except:
                        published = datetime.now()
                else:
                    published = datetime.now()

                # Only include recent tweets (within 24 hours)
                if (datetime.now() - published.replace(tzinfo=None)) > timedelta(hours=24):
                    continue

                article_id = hashlib.md5(link.encode()).hexdigest()

                article = {
                    'id': article_id,
                    'title': f"@{username}: {title}",
                    'link': link,
                    'published': published,
                    'summary': title,
                    'source': f"Twitter @{username}",
                    'source_category': 'social_media',
                    'authority_score': authority_score,
                    'fetch_time': datetime.now()
                }
                articles.append(article)

            except Exception as e:
                logger.debug(f"Error parsing tweet: {e}")
                continue

        logger.info(f"Fetched {len(articles)} tweets from @{username}")

    except Exception as e:
        logger.error(f"Error scraping @{username}: {e}")

    finally:
        if playwright:
            playwright.stop()

    return articles


def scrape_all_twitter_accounts(max_tweets_per_account=10):
    """
    Scrape tweets from all configured Twitter accounts

    Args:
        max_tweets_per_account: Maximum tweets per account

    Returns:
        list: Combined list of tweet articles
    """
    all_articles = []

    # Import here to avoid dependency issues if not needed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return []

    playwright = None
    browser = None

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.contexts[0]

        for account in TWITTER_ACCOUNTS:
            username = account['username']
            authority_score = account['authority_score']

            try:
                page = context.new_page()

                url = f"https://twitter.com/{username}"
                logger.info(f"Scraping Twitter: @{username}")

                page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                })

                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_selector('article', timeout=10000)

                # Scroll to load more tweets
                for _ in range(2):
                    page.mouse.wheel(0, 300)
                    page.wait_for_timeout(800)

                tweets = page.query_selector_all('article')

                for tweet in tweets[:max_tweets_per_account]:
                    try:
                        text_elem = tweet.query_selector('div[data-testid="tweetText"]')
                        if not text_elem:
                            continue
                        title = text_elem.inner_text()[:200]

                        link_elem = tweet.query_selector('a[href*="/status/"]')
                        if not link_elem:
                            continue
                        link = link_elem.get_attribute('href')
                        if not link.startswith('http'):
                            link = f"https://twitter.com{link}"

                        time_elem = tweet.query_selector('time')
                        if time_elem:
                            datetime_str = time_elem.get_attribute('datetime')
                            try:
                                published = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            except:
                                published = datetime.now()
                        else:
                            published = datetime.now()

                        # Only include recent tweets
                        if (datetime.now() - published.replace(tzinfo=None)) > timedelta(hours=48):
                            continue

                        article_id = hashlib.md5(link.encode()).hexdigest()

                        article = {
                            'id': article_id,
                            'title': f"@{username}: {title}",
                            'link': link,
                            'published': published,
                            'summary': title,
                            'source': f"Twitter @{username}",
                            'source_category': 'social_media',
                            'authority_score': authority_score,
                            'fetch_time': datetime.now()
                        }
                        all_articles.append(article)

                    except Exception as e:
                        continue

                logger.info(f"Fetched tweets from @{username}")
                page.close()

                # Random delay between accounts
                import time
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                logger.error(f"Error scraping @{username}: {e}")
                continue

    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()

    logger.info(f"Total tweets fetched: {len(all_articles)}")
    return all_articles


def scrape_twitter_with_context():
    """
    Alternative approach: create a new context explicitly
    Returns list of articles
    """
    from playwright.sync_api import sync_playwright

    all_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create explicit context with viewport
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        for account in TWITTER_ACCOUNTS:
            username = account['username']
            authority_score = account['authority_score']

            try:
                page = context.new_page()

                url = f"https://twitter.com/{username}"
                logger.info(f"Scraping Twitter: @{username}")

                page.goto(url, wait_until='domcontentloaded', timeout=30000)

                # Try to wait for article element
                try:
                    page.wait_for_selector('article', timeout=10000)
                except:
                    logger.warning(f"No tweets found for @{username}")
                    page.close()
                    continue

                # Scroll to load more
                for _ in range(2):
                    page.mouse.wheel(0, 300)
                    page.wait_for_timeout(800)

                tweets = page.query_selector_all('article')

                for tweet in tweets[:10]:
                    try:
                        text_elem = tweet.query_selector('div[data-testid="tweetText"]')
                        if not text_elem:
                            continue
                        title = text_elem.inner_text()[:200]

                        link_elem = tweet.query_selector('a[href*="/status/"]')
                        if not link_elem:
                            continue
                        link = link_elem.get_attribute('href')
                        if not link.startswith('http'):
                            link = f"https://twitter.com{link}"

                        time_elem = tweet.query_selector('time')
                        if time_elem:
                            datetime_str = time_elem.get_attribute('datetime')
                            try:
                                published = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            except:
                                published = datetime.now()
                        else:
                            published = datetime.now()

                        # Only include recent tweets (48 hours)
                        if (datetime.now() - published.replace(tzinfo=None)) > timedelta(hours=48):
                            continue

                        article_id = hashlib.md5(link.encode()).hexdigest()

                        article = {
                            'id': article_id,
                            'title': f"@{username}: {title}",
                            'link': link,
                            'published': published,
                            'summary': title,
                            'source': f"Twitter @{username}",
                            'source_category': 'social_media',
                            'authority_score': authority_score,
                            'fetch_time': datetime.now()
                        }
                        all_articles.append(article)

                    except Exception as e:
                        continue

                logger.info(f"Fetched from @{username}")
                page.close()

                import time
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                logger.error(f"Error scraping @{username}: {e}")
                continue

        context.close()
        browser.close()

    return all_articles


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("Testing Twitter scraper...")
    articles = scrape_twitter_with_context()

    print(f"\nFetched {len(articles)} tweets")
    for article in articles[:5]:
        print(f"  - {article['title'][:80]}...")
