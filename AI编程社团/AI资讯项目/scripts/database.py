#!/usr/bin/env python3
"""
Database Module
SQLite database operations for article storage
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ArticleDatabase:
    """SQLite database for article storage"""

    def __init__(self, db_path):
        """
        Initialize database connection

        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Create database and tables if they don't exist"""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # Create articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                published TIMESTAMP,
                summary TEXT,
                source TEXT,
                source_category TEXT,
                category TEXT,
                authority_score REAL,
                score REAL,
                fetch_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_published
            ON articles(published DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_score
            ON articles(score DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category
            ON articles(category)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON articles(created_at DESC)
        ''')

        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")

    def save_articles(self, articles):
        """
        Save articles to database (insert or update)

        Args:
            articles (list): List of article dictionaries

        Returns:
            tuple: (inserted_count, updated_count)
        """
        cursor = self.conn.cursor()
        inserted = 0
        updated = 0

        for article in articles:
            try:
                # Convert datetime to string
                published_str = article['published'].isoformat() if isinstance(
                    article['published'], datetime) else article['published']
                fetch_time_str = article['fetch_time'].isoformat() if isinstance(
                    article['fetch_time'], datetime) else article['fetch_time']

                # Try to insert
                cursor.execute('''
                    INSERT OR REPLACE INTO articles
                    (id, title, link, published, summary, source, source_category,
                     category, authority_score, score, fetch_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['id'],
                    article['title'],
                    article['link'],
                    published_str,
                    article.get('summary', ''),
                    article['source'],
                    article.get('source_category', 'unknown'),
                    article.get('category', '其他'),
                    article.get('authority_score', 20),
                    article.get('score', 0),
                    fetch_time_str
                ))

                if cursor.rowcount > 0:
                    inserted += 1

            except sqlite3.IntegrityError:
                updated += 1
                logger.debug(f"Article already exists: {article['title']}")
            except Exception as e:
                logger.error(f"Error saving article {article.get('id', 'unknown')}: {e}")

        self.conn.commit()
        logger.info(f"Saved articles: {inserted} inserted, {updated} updated")
        return (inserted, updated)

    def get_recent_articles(self, hours=24, limit=100):
        """
        Get recent articles within specified hours

        Args:
            hours (int): Number of hours to look back
            limit (int): Maximum number of articles

        Returns:
            list: List of article dictionaries
        """
        cursor = self.conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()

        cursor.execute('''
            SELECT * FROM articles
            WHERE published >= ?
            ORDER BY score DESC, published DESC
            LIMIT ?
        ''', (cutoff_str, limit))

        articles = []
        for row in cursor.fetchall():
            article = dict(row)
            # Convert string back to datetime
            article['published'] = datetime.fromisoformat(article['published'])
            article['fetch_time'] = datetime.fromisoformat(article['fetch_time'])
            articles.append(article)

        logger.info(f"Retrieved {len(articles)} articles from last {hours} hours")
        return articles

    def get_today_articles(self, limit=100):
        """
        Get today's articles

        Args:
            limit (int): Maximum number of articles

        Returns:
            list: List of article dictionaries
        """
        return self.get_recent_articles(hours=24, limit=limit)

    def get_articles_by_category(self, category, hours=24, limit=50):
        """
        Get articles filtered by category

        Args:
            category (str): Category name
            hours (int): Number of hours to look back
            limit (int): Maximum number of articles

        Returns:
            list: List of article dictionaries
        """
        cursor = self.conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()

        cursor.execute('''
            SELECT * FROM articles
            WHERE category = ? AND published >= ?
            ORDER BY score DESC, published DESC
            LIMIT ?
        ''', (category, cutoff_str, limit))

        articles = []
        for row in cursor.fetchall():
            article = dict(row)
            article['published'] = datetime.fromisoformat(article['published'])
            article['fetch_time'] = datetime.fromisoformat(article['fetch_time'])
            articles.append(article)

        return articles

    def cleanup_old_articles(self, days=30):
        """
        Delete articles older than specified days

        Args:
            days (int): Number of days to retain

        Returns:
            int: Number of deleted articles
        """
        cursor = self.conn.cursor()

        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_time.isoformat()

        cursor.execute('''
            DELETE FROM articles
            WHERE created_at < ?
        ''', (cutoff_str,))

        deleted_count = cursor.rowcount
        self.conn.commit()

        logger.info(f"Cleaned up {deleted_count} old articles (older than {days} days)")
        return deleted_count

    def get_stats(self):
        """
        Get database statistics

        Returns:
            dict: Statistics dictionary
        """
        cursor = self.conn.cursor()

        # Total articles
        cursor.execute('SELECT COUNT(*) as count FROM articles')
        total = cursor.fetchone()['count']

        # Today's articles
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as count FROM articles
            WHERE published >= ?
        ''', (cutoff,))
        today = cursor.fetchone()['count']

        # Articles by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM articles
            WHERE published >= ?
            GROUP BY category
            ORDER BY count DESC
        ''', (cutoff,))
        categories = {row['category']: row['count'] for row in cursor.fetchall()}

        # Top sources
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM articles
            WHERE published >= ?
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        ''', (cutoff,))
        sources = {row['source']: row['count'] for row in cursor.fetchall()}

        return {
            'total_articles': total,
            'today_articles': today,
            'categories': categories,
            'top_sources': sources
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == '__main__':
    # Test database
    logging.basicConfig(level=logging.INFO)

    db = ArticleDatabase('data/test_ai_news.db')

    # Test save
    test_articles = [
        {
            'id': 'test1',
            'title': 'Test Article 1',
            'link': 'https://example.com/1',
            'published': datetime.now(),
            'summary': 'Test summary',
            'source': 'Test Source',
            'source_category': 'test',
            'category': '技术突破',
            'authority_score': 25,
            'score': 85.5,
            'fetch_time': datetime.now()
        }
    ]

    db.save_articles(test_articles)

    # Test retrieve
    articles = db.get_today_articles()
    print(f"Retrieved {len(articles)} articles")

    # Test stats
    stats = db.get_stats()
    print(f"Stats: {stats}")

    db.close()
