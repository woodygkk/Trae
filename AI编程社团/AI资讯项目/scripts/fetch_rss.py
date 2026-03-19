#!/usr/bin/env python3
"""
RSS Feed Fetching Module
Fetches articles from configured RSS sources
"""

import feedparser
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


def fetch_rss_source(source_config):
    """
    Fetch articles from a single RSS source

    Args:
        source_config (dict): Source configuration with url, name, etc.

    Returns:
        list: List of article dictionaries
    """
    try:
        url = source_config['url']
        logger.info(f"Fetching RSS from: {source_config['name']}")

        feed = feedparser.parse(url)

        if feed.bozo:
            logger.warning(f"RSS parse warning for {source_config['name']}: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries:
            # Generate unique ID from URL
            article_id = hashlib.md5(entry.link.encode()).hexdigest()

            # Parse published time
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    pass

            if not published:
                published = datetime.now()

            article = {
                'id': article_id,
                'title': entry.get('title', 'No Title'),
                'link': entry.link,
                'published': published,
                'summary': entry.get('summary', entry.get('description', '')),
                'source': source_config['name'],
                'source_category': source_config.get('category', 'unknown'),
                'authority_score': source_config.get('authority_score', 20),
                'fetch_time': datetime.now()
            }

            articles.append(article)

        logger.info(f"Fetched {len(articles)} articles from {source_config['name']}")
        return articles

    except Exception as e:
        logger.error(f"Error fetching {source_config.get('name', 'unknown')}: {e}")
        return []


def fetch_all_sources(sources_list, max_workers=10):
    """
    Fetch articles from all sources in parallel

    Args:
        sources_list (list): List of source configurations
        max_workers (int): Maximum number of parallel workers

    Returns:
        list: Combined list of all articles
    """
    all_articles = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_source = {
            executor.submit(fetch_rss_source, source): source
            for source in sources_list
        }

        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Exception for {source.get('name', 'unknown')}: {e}")

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles


def fetch_github_trending():
    """
    Fetch trending repositories from GitHub
    Note: This is a placeholder - implement if GitHub API is needed
    """
    # TODO: Implement GitHub API fetching
    pass


def fetch_arxiv_papers(category='cs.AI', max_results=20):
    """
    Fetch recent papers from arXiv

    Args:
        category (str): arXiv category
        max_results (int): Maximum number of results

    Returns:
        list: List of paper articles
    """
    try:
        import urllib.parse

        query = f'cat:{category}'
        url = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'

        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries:
            article_id = hashlib.md5(entry.id.encode()).hexdigest()

            published = None
            if hasattr(entry, 'published_parsed'):
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    published = datetime.now()

            article = {
                'id': article_id,
                'title': entry.title,
                'link': entry.link,
                'published': published or datetime.now(),
                'summary': entry.get('summary', ''),
                'source': f'arXiv {category}',
                'source_category': 'academic',
                'authority_score': 28,
                'fetch_time': datetime.now()
            }

            articles.append(article)

        logger.info(f"Fetched {len(articles)} papers from arXiv {category}")
        return articles

    except Exception as e:
        logger.error(f"Error fetching arXiv: {e}")
        return []


if __name__ == '__main__':
    # Test fetching
    logging.basicConfig(level=logging.INFO)

    test_source = {
        'name': 'TechCrunch AI',
        'url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'category': 'tech_media',
        'authority_score': 25
    }

    articles = fetch_rss_source(test_source)
    print(f"Fetched {len(articles)} articles")
    if articles:
        print(f"Sample: {articles[0]['title']}")
