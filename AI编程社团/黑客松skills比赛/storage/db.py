# -*- coding: utf-8 -*-
"""
数据存储模块
使用SQLite本地数据库
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """SQLite数据库操作"""

    def __init__(self, db_path: str = "data/articles.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建话题表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                platform TEXT,
                hot_score INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        """)

        # 创建文章表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                title TEXT,
                content TEXT,
                platform TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT,
                published_at TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)

        conn.commit()
        conn.close()

    def save_topic(self, topic: str, platform: str, hot_score: int = 0) -> int:
        """保存话题"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO topics (title, platform, hot_score, created_at) VALUES (?, ?, ?, ?)",
            (topic, platform, hot_score, datetime.now().isoformat())
        )

        topic_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return topic_id

    def save_article(self, topic_id: int, title: str, content: str, platform: str) -> int:
        """保存文章"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO articles (topic_id, title, content, platform, created_at) VALUES (?, ?, ?, ?, ?)",
            (topic_id, title, content, platform, datetime.now().isoformat())
        )

        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id

    def get_topics(self, limit: int = 50, status: str = None) -> List[Dict]:
        """获取话题列表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM topics WHERE status = ? ORDER BY hot_score DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM topics ORDER BY hot_score DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_articles(self, limit: int = 20, status: str = None) -> List[Dict]:
        """获取文章列表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM articles WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM articles ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_topic_status(self, topic_id: int, status: str):
        """更新话题状态"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE topics SET status = ? WHERE id = ?",
            (status, topic_id)
        )

        conn.commit()
        conn.close()

    def update_article_status(self, article_id: int, status: str):
        """更新文章状态"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status == "published":
            cursor.execute(
                "UPDATE articles SET status = ?, published_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), article_id)
            )
        else:
            cursor.execute(
                "UPDATE articles SET status = ? WHERE id = ?",
                (status, article_id)
            )

        conn.commit()
        conn.close()


if __name__ == "__main__":
    # 测试
    db = Database()
    topics = db.get_topics(5)
    print(f"数据库中有 {len(topics)} 个话题")
