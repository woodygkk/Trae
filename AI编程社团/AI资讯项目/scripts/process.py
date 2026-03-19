#!/usr/bin/env python3
"""
Content Processing Module
Handles deduplication, classification, and ranking
"""

import re
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Category definitions with keywords
CATEGORIES = {
    '技术突破': {
        'keywords': ['breakthrough', 'state-of-art', 'sota', 'achieves', 'new model',
                    'outperforms', 'surpasses', 'record', 'first time', 'revolutionary',
                    '突破', '最新', '最强', '超越', '创新', '首款', '首发', '全球首'],
        'weight': 1.2
    },
    '产品发布': {
        'keywords': ['launches', 'releases', 'announces', 'available', 'unveils',
                    'introduces', 'beta', 'shipping', 'now live', 'debuts',
                    '发布', '上线', '推出', '新品', '正式版', '公测', '内测', '开放'],
        'weight': 1.1
    },
    '研究论文': {
        'keywords': ['paper', 'arxiv', 'research', 'study', 'published', 'conference',
                    'neurips', 'icml', 'cvpr', 'iclr', 'findings', 'preprint',
                    '论文', '研究', '顶会', 'arxiv', '预印本', '成果'],
        'weight': 1.0
    },
    '行业动态': {
        'keywords': ['funding', 'raises', 'acquires', 'partnership', 'hires', 'appoints',
                    'series a', 'series b', 'valuation', 'ipo', 'merger', 'investment',
                    '融资', '投资', '收购', '并购', '上市', '估值', '合作', '招聘'],
        'weight': 0.9
    },
    '政策法规': {
        'keywords': ['regulation', 'policy', 'law', 'ethics', 'governance', 'ban',
                    'restrict', 'compliance', 'lawsuit', 'legal', 'court',
                    '监管', '政策', '法规', '禁止', '限制', '合规', '法律'],
        'weight': 0.85
    },
    '工具教程': {
        'keywords': ['tutorial', 'guide', 'how to', 'tool', 'library', 'framework',
                    'api', 'documentation', 'getting started', 'introduction',
                    '教程', '指南', '工具', '框架', 'API', '文档', '开源'],
        'weight': 0.7
    }
}


def deduplicate_by_url(articles):
    """
    Remove duplicate articles by URL

    Args:
        articles (list): List of article dictionaries

    Returns:
        list: Deduplicated articles
    """
    seen_urls = set()
    seen_ids = set()
    unique_articles = []

    for article in articles:
        url = article.get('link', '')
        article_id = article.get('id', '')

        if url not in seen_urls and article_id not in seen_ids:
            seen_urls.add(url)
            seen_ids.add(article_id)
            unique_articles.append(article)

    logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
    return unique_articles


def calculate_title_similarity(title1, title2):
    """
    Calculate similarity between two titles (simple word overlap)

    Args:
        title1 (str): First title
        title2 (str): Second title

    Returns:
        float: Similarity score (0-1)
    """
    words1 = set(re.findall(r'\w+', title1.lower()))
    words2 = set(re.findall(r'\w+', title2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def deduplicate_by_similarity(articles, threshold=0.7):
    """
    Remove near-duplicate articles by title similarity

    Args:
        articles (list): List of article dictionaries
        threshold (float): Similarity threshold (0-1)

    Returns:
        list: Deduplicated articles
    """
    unique_articles = []

    for article in articles:
        is_duplicate = False

        for existing in unique_articles:
            similarity = calculate_title_similarity(
                article['title'],
                existing['title']
            )

            if similarity >= threshold:
                is_duplicate = True
                # Keep the one with higher authority score
                if article['authority_score'] > existing['authority_score']:
                    unique_articles.remove(existing)
                    unique_articles.append(article)
                break

        if not is_duplicate:
            unique_articles.append(article)

    logger.info(f"Similarity dedup: {len(articles)} -> {len(unique_articles)} articles")
    return unique_articles


def classify_article(article):
    """
    Classify article into categories based on keywords

    Args:
        article (dict): Article dictionary

    Returns:
        str: Category name
    """
    title = article.get('title', '').lower()
    summary = article.get('summary', '').lower()
    text = title + ' ' + summary

    # Score each category
    category_scores = {}
    for category, config in CATEGORIES.items():
        keywords = config['keywords']
        weight = config['weight']

        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in text)
        category_scores[category] = matches * weight

    # Return category with highest score
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1])
        if best_category[1] > 0:
            return best_category[0]

    return '其他'


def calculate_article_score(article):
    """
    Calculate multi-dimensional score for article

    Args:
        article (dict): Article dictionary

    Returns:
        float: Article score (0-100)
    """
    score = 0.0

    # 1. Time freshness score (0-40 points)
    published = article['published']
    # Handle timezone-aware datetimes from Twitter
    if published.tzinfo is not None:
        published = published.replace(tzinfo=None)
    age_hours = (datetime.now() - published).total_seconds() / 3600
    time_score = 40 / (1 + age_hours / 24)  # Decay over 24 hours
    score += time_score

    # 2. Authority score (0-30 points)
    authority_score = min(article.get('authority_score', 20), 30)
    score += authority_score

    # 3. Title excitement score (0-20 points)
    title = article.get('title', '').lower()
    excitement_keywords = [
        'breakthrough', 'first', 'launches', 'achieves', 'new',
        'revolutionary', 'unveils', 'announces', 'major', 'significant',
        # 大模型关键词
        'gpt', 'claude', 'gemini', 'deepseek', 'llama', 'mistral',
        'openai', 'anthropic', 'google', 'meta ai', 'alphafold',
        'o1', 'o3', 'gpt-4', 'gpt-5', 'sonnet', 'opus',
        '重磅', '炸裂', '爆火', '颠覆', '史上最强', '王炸',
        'v4', 'v5', 'v3', '4o', '4v', '4.5', '5.0'
    ]
    excitement_score = sum(4 for kw in excitement_keywords if kw in title)
    excitement_score = min(excitement_score, 20)
    score += excitement_score

    # 4. Content richness score (0-10 points)
    summary_length = len(article.get('summary', ''))
    content_score = min(summary_length / 50, 10)
    score += content_score

    # Apply category weight
    category = article.get('category', '其他')
    category_weight = CATEGORIES.get(category, {}).get('weight', 1.0)
    score *= category_weight

    return round(score, 2)


def rank_articles(articles):
    """
    Rank articles by calculated score

    Args:
        articles (list): List of article dictionaries

    Returns:
        list: Sorted articles (highest score first)
    """
    for article in articles:
        article['score'] = calculate_article_score(article)

    sorted_articles = sorted(articles, key=lambda x: x['score'], reverse=True)

    logger.info(f"Ranked {len(sorted_articles)} articles")
    if sorted_articles:
        logger.info(f"Top score: {sorted_articles[0]['score']}, "
                   f"Bottom score: {sorted_articles[-1]['score']}")

    return sorted_articles


def process_articles(articles):
    """
    Complete processing pipeline: deduplicate, classify, rank

    Args:
        articles (list): Raw articles from fetcher

    Returns:
        list: Processed and ranked articles
    """
    logger.info(f"Starting processing of {len(articles)} articles")

    # Step 1: Deduplicate by URL
    articles = deduplicate_by_url(articles)

    # Step 2: Deduplicate by similarity
    articles = deduplicate_by_similarity(articles, threshold=0.7)

    # Step 3: Classify
    for article in articles:
        article['category'] = classify_article(article)

    # Step 4: Rank
    articles = rank_articles(articles)

    logger.info(f"Processing complete: {len(articles)} articles ready")
    return articles


if __name__ == '__main__':
    # Test processing
    logging.basicConfig(level=logging.INFO)

    test_articles = [
        {
            'id': '1',
            'title': 'OpenAI Launches GPT-5 with Breakthrough Performance',
            'link': 'https://example.com/1',
            'published': datetime.now(),
            'summary': 'OpenAI announces GPT-5...',
            'source': 'OpenAI',
            'authority_score': 30
        },
        {
            'id': '2',
            'title': 'New Research Paper on Machine Learning',
            'link': 'https://example.com/2',
            'published': datetime.now(),
            'summary': 'A research paper published on arXiv...',
            'source': 'arXiv',
            'authority_score': 28
        }
    ]

    processed = process_articles(test_articles)
    for article in processed:
        print(f"{article['title']}: {article['category']}, Score: {article['score']}")
