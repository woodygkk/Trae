#!/usr/bin/env python3
"""
AI News Skill - Main Entry Point
Aggregates and delivers top AI news daily
"""

import sys
import os
import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fetch_rss import fetch_all_sources, fetch_arxiv_papers
from fetch_twitter import scrape_twitter_with_context
from process import process_articles
from push import push_to_channels, format_for_markdown
from database import ArticleDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'ai_news.log')
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_name):
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / 'config' / f'{config_name}.yaml'

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def fetch_articles():
    """Fetch articles from all sources"""
    logger.info("Starting article fetch...")

    # Load sources config
    sources_config = load_config('sources')

    all_articles = []

    # Fetch from RSS feeds
    rss_feeds = sources_config.get('rss_feeds', [])
    enabled_feeds = [feed for feed in rss_feeds if feed.get('enabled', True)]

    if enabled_feeds:
        logger.info(f"Fetching from {len(enabled_feeds)} RSS sources...")
        rss_articles = fetch_all_sources(enabled_feeds)
        all_articles.extend(rss_articles)

    # Fetch from arXiv if enabled
    api_sources = sources_config.get('api_sources', {})
    arxiv_config = api_sources.get('arxiv', {})

    if arxiv_config.get('enabled'):
        logger.info("Fetching from arXiv...")
        for category in arxiv_config.get('categories', ['cs.AI']):
            max_results = arxiv_config.get('max_results', 20)
            arxiv_articles = fetch_arxiv_papers(category, max_results)
            all_articles.extend(arxiv_articles)

    # Fetch from Twitter if enabled (in api_sources.twitter)
    twitter_config = api_sources.get('twitter', {})
    if twitter_config.get('enabled', False):
        logger.info("Fetching from Twitter...")
        max_tweets = twitter_config.get('max_tweets_per_account', 10)
        twitter_articles = scrape_twitter_with_context()
        all_articles.extend(twitter_articles)

    logger.info(f"Total raw articles fetched: {len(all_articles)}")
    return all_articles


def update_database():
    """Fetch new articles and update database"""
    logger.info("=== Starting Update ===")

    # Initialize database
    db_path = Path(__file__).parent.parent / 'data' / 'ai_news.db'
    db = ArticleDatabase(str(db_path))

    # Fetch articles
    articles = fetch_articles()

    if not articles:
        logger.warning("No articles fetched")
        return

    # Process articles
    processed = process_articles(articles)

    # Save to database
    inserted, updated = db.save_articles(processed)

    logger.info(f"Database updated: {inserted} new, {updated} updated")

    # Cleanup old articles
    settings = load_config('sources').get('settings', {})
    retention_days = settings.get('retention_days', 30)
    deleted = db.cleanup_old_articles(retention_days)

    # Show stats
    stats = db.get_stats()
    logger.info(f"Database stats: {stats}")

    db.close()
    logger.info("=== Update Complete ===")


def show_today(count=10, category=None, format_type='markdown'):
    """Show today's top news"""
    # Initialize database
    db_path = Path(__file__).parent.parent / 'data' / 'ai_news.db'
    db = ArticleDatabase(str(db_path))

    # Get articles
    if category:
        articles = db.get_articles_by_category(category, hours=24, limit=count)
    else:
        articles = db.get_today_articles(limit=count)

    db.close()

    if not articles:
        print("No articles found for today. Run 'update' first.")
        return

    # Format output
    if format_type == 'json':
        import json
        print(json.dumps([
            {
                'title': a['title'],
                'link': a['link'],
                'source': a['source'],
                'category': a['category'],
                'score': a['score'],
                'published': a['published'].isoformat()
            }
            for a in articles[:count]
        ], indent=2, ensure_ascii=False))
    else:
        # Markdown format
        content = format_for_markdown(articles, count)
        print(content)


def push_news(count=10):
    """Push news to configured channels"""
    logger.info("=== Starting Push ===")

    # Load push config
    push_config = load_config('push')

    if not push_config:
        logger.error("Push configuration not found")
        return

    # Get articles from database
    db_path = Path(__file__).parent.parent / 'data' / 'ai_news.db'
    db = ArticleDatabase(str(db_path))

    articles = db.get_today_articles(limit=count)
    db.close()

    if not articles:
        logger.warning("No articles to push")
        return

    # Push to channels
    results = push_to_channels(articles, push_config, count)

    # Log results
    for channel, result in results:
        status = "Success" if result.get('code') == 0 or result.get('ok') or result.get('status') == 'success' else "Failed"
        logger.info(f"[{channel}] {status}: {result}")

    logger.info("=== Push Complete ===")


def show_stats():
    """Show database statistics"""
    db_path = Path(__file__).parent.parent / 'data' / 'ai_news.db'
    db = ArticleDatabase(str(db_path))

    stats = db.get_stats()
    db.close()

    print("\n=== AI News Statistics ===\n")
    print(f"Total Articles: {stats['total_articles']}")
    print(f"Today's Articles: {stats['today_articles']}")

    print("\nArticles by Category:")
    for cat, count in stats['categories'].items():
        print(f"  {cat}: {count}")

    print("\nTop Sources (Today):")
    for source, count in stats['top_sources'].items():
        print(f"  {source}: {count}")
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AI News Skill - Aggregates and delivers top AI news',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s update              # Fetch and update articles
  %(prog)s today               # Show today's top 10 news
  %(prog)s today --count 20    # Show top 20 news
  %(prog)s today --category 技术突破  # Filter by category
  %(prog)s push                # Push to configured channels
  %(prog)s stats               # Show statistics
        '''
    )

    parser.add_argument('command',
                       choices=['update', 'today', 'push', 'stats'],
                       help='Command to execute')

    parser.add_argument('--count', type=int, default=10,
                       help='Number of articles to show (default: 10)')

    parser.add_argument('--category', type=str,
                       help='Filter by category')

    parser.add_argument('--format', choices=['markdown', 'json'],
                       default='markdown',
                       help='Output format (default: markdown)')

    args = parser.parse_args()

    try:
        if args.command == 'update':
            update_database()

        elif args.command == 'today':
            show_today(args.count, args.category, args.format)

        elif args.command == 'push':
            push_news(args.count)

        elif args.command == 'stats':
            show_stats()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
