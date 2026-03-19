# -*- coding: utf-8 -*-
"""
公众号爆款内容创作系统 - 命令行版
主程序入口

使用方法:
    hot 或 -hot                - 获取今日热点
    write 1 或 -w 1            - 选择话题编号写文章
    list 或 -l                 - 查看历史文章
    copy 1 或 -c 1            - 复制历史文章
    help 或 -h                 - 查看帮助
"""

import sys
import pyperclip
from services import HotTopicService, AIWriter, ArticleService
from storage import Database


# 命令映射表
COMMANDS = {
    # 英文命令
    "hot": "hot",
    "search": "search",  # 搜索关键词
    "write": "write",
    "list": "list",
    "copy": "copy",
    "publish": "publish",
    "gen": "gen",
    "image": "image",  # 生成配图
    "help": "help",
    # 短参数
    "-h": "help",
    "-s": "search",
    "-w": "write",
    "-l": "list",
    "-c": "copy",
    "-p": "publish",
    "-g": "gen",
    "-i": "image",
}


def print_banner():
    """打印欢迎横幅"""
    print("=" * 50)
    print("  公众号爆款内容创作系统")
    print("  每天5分钟，AI帮你写爆款")
    print("=" * 50)
    print()


def cmd_hot():
    """获取今日热点"""
    print("\n=== 获取今日热点 ===\n")

    service = HotTopicService()
    topics = service.get_all_topics()

    if not topics:
        print("获取热点失败，请检查网络连接")
        return None

    print("\n=== 今日热门话题排行榜 ===\n")
    for i, topic in enumerate(topics[:15], 1):
        print(f"  {i:2d}. [{topic['platform']}] {topic['title']}")
        print(f"      热度: {topic['hot_score']}")
        print()

    print("=" * 50)
    print("要写文章？请运行: write 1")
    print("例如: python main.py write 1")
    print("=" * 50)

    return topics


def cmd_search(keyword: str = None):
    """搜索关键词并生成文章"""
    print("\n=== 搜索并生成文章 ===\n")

    # 获取用户输入的关键词
    if not keyword:
        print("请输入你想写的话题关键词：")
        keyword = input("> ").strip()

    if not keyword:
        print("关键词不能为空")
        return

    print(f"主题: {keyword}")
    print("\n1. 搜索相关信息...")

    # 导入AI来搜索和提取观点
    from services.ai_writer import AISearcher

    searcher = AISearcher()
    print("   正在搜索并提取观点...")

    # 获取搜索结果和观点
    search_result = searcher.search_and_extract(keyword)

    if not search_result:
        print("搜索失败，请换个关键词试试")
        return

    # 显示搜索到的信息
    print("\n=== 搜索到的热点 ===")
    for i, info in enumerate(search_result.get('highlights', [])[:5], 1):
        print(f"  {i}. {info}")
    print()

    # 显示提取的观点
    print("=== AI提取的观点 ===")
    for i, point in enumerate(search_result.get('points', []), 1):
        print(f"  {i}. {point}")
    print()

    print("2. 正在生成风格化文章...")

    # 生成文章
    from services.ai_writer import generate_from_search
    article = generate_from_search(keyword, search_result)

    # 保存文章
    article_service = ArticleService()
    filepath = article_service.save_article(keyword, "搜索", article)

    # 复制到剪贴板
    pyperclip.copy(article)

    print("=" * 50)
    print("[OK] 文章已生成并复制到剪贴板！")
    print(f"   主题: {keyword}")
    print(f"   保存: {filepath}")
    print("   请到公众号粘贴发布")
    print("=" * 50)


def cmd_write(topic_index: int = None):
    """写文章"""
    service = HotTopicService()
    topics = service.get_all_topics()

    if not topics:
        print("获取热点失败")
        return

    # 如果没有指定编号，先显示热点让用户选择
    if topic_index is None:
        print("\n请先运行 hot 查看热点话题")
        print("然后用 write <编号> 来写文章")
        print("例如: python main.py write 1")
        return

    index = topic_index - 1
    if index < 0 or index >= len(topics):
        print(f"话题编号无效，请选择1-{len(topics)}之间的数字")
        return

    topic = topics[index]
    print(f"\n你选择的话题: {topic['title']}")
    print(f"来源平台: {topic['platform']}")
    print("\n正在让AI为你写文章，请稍候...\n")

    # AI写文章
    writer = AIWriter()
    article_content = writer.generate_article(topic['title'], topic['platform'])

    # 保存文章
    article_service = ArticleService()
    filepath = article_service.save_article(
        topic['title'],
        topic['platform'],
        article_content
    )

    # 保存到数据库
    db = Database()
    topic_id = db.save_topic(topic['title'], topic['platform'], topic['hot_score'])
    db.save_article(topic_id, topic['title'], article_content, topic['platform'])

    # 复制到剪贴板
    print("\n正在复制到剪贴板...")
    pyperclip.copy(article_content)
    print("=" * 50)
    print("✅ 文章已复制到剪贴板！")
    print("   请打开公众号后台粘贴发布")
    print(f"   文章已保存到: {filepath}")
    print("=" * 50)


def cmd_list():
    """显示历史文章"""
    print("\n=== 历史文章列表 ===\n")

    service = ArticleService()
    articles = service.list_articles()

    if not articles:
        print("还没有文章，快去写一篇吧！")
        return

    for i, article in enumerate(articles, 1):
        print(f"  {i}. {article['topic']}")
        print(f"     生成时间: {article['created_at']}")
        print()

    print("=" * 50)
    print("复制历史文章？运行: copy <编号>")
    print("例如: python main.py copy 1")
    print("=" * 50)


def cmd_copy(article_index: int):
    """复制历史文章"""
    service = ArticleService()
    articles = service.list_articles()

    if not articles:
        print("没有可复制的文章")
        return

    index = article_index - 1
    if index < 0 or index >= len(articles):
        print(f"文章编号无效，请选择1-{len(articles)}之间的数字")
        return

    article = articles[index]
    content = service.read_article(article['filepath'])

    if content:
        pyperclip.copy(content)
        print("=" * 50)
        print(f"✅ 已复制: {article['topic']}")
        print("   请到公众号后台粘贴")
        print("=" * 50)


def cmd_gen(topic_index: int = None):
    """快速生成文章：获取热点 + AI写文章 + 复制到剪贴板"""
    print("\n=== 快速生成文章 ===\n")

    # 获取热点
    print("1. 获取今日热点...")
    service = HotTopicService()
    topics = service.get_all_topics()

    if not topics:
        print("获取热点失败")
        return

    # 如果没有指定话题，让用户选择
    if topic_index is None:
        print("\n热门话题：")
        for i, topic in enumerate(topics[:10], 1):
            print(f"  {i}. [{topic['platform']}] {topic['title']}")
        print()
        try:
            choice = input("选择话题编号: ")
            topic_index = int(choice)
        except ValueError:
            print("无效选择")
            return

    index = topic_index - 1
    if index < 0 or index >= len(topics):
        print("编号无效")
        return

    topic = topics[index]
    print(f"\n2. 选择话题: {topic['title']}")
    print("   正在让AI生成文章...")

    # AI写文章
    writer = AIWriter()
    article_content = writer.generate_article(topic['title'], topic['platform'])

    # 保存文章
    article_service = ArticleService()
    filepath = article_service.save_article(
        topic['title'],
        topic['platform'],
        article_content
    )

    # 复制到剪贴板
    print("\n3. 复制到剪贴板...")
    pyperclip.copy(article_content)

    print("=" * 50)
    print("[OK] 文章已生成并复制到剪贴板！")
    print(f"   话题: {topic['title']}")
    print(f"   保存: {filepath}")
    print("   请到公众号粘贴发布")
    print("=" * 50)


def cmd_publish(article_index: int = None):
    """发布文章到公众号草稿箱"""
    service = ArticleService()
    articles = service.list_articles()

    if not articles:
        print("没有可发布的文章")
        print("请先运行: python main.py write 1")
        return

    # 如果没有指定编号，让用户选择
    if article_index is None:
        print("\n请选择要发布的文章编号：")
        for i, article in enumerate(articles[:5], 1):
            print(f"  {i}. {article['topic']}")
        print()
        try:
            choice = input("请输入编号: ")
            article_index = int(choice)
        except ValueError:
            print("无效编号")
            return

    index = article_index - 1
    if index < 0 or index >= len(articles):
        print(f"文章编号无效，请选择1-{len(articles)}之间的数字")
        return

    article = articles[index]
    content = service.read_article(article['filepath'])

    if content:
        # 从内容中提取标题（去掉开头的元信息）
        lines = content.split('\n')
        title = article['topic']
        for line in lines:
            if line.startswith('标题：'):
                title = line.replace('标题：', '').strip()
                break

        print(f"\n正在发布: {title}")
        print("将打开浏览器，请扫码登录微信公众号...")

        # 导入发布服务
        try:
            from services.wechat_publisher import publish_article
            publish_article(title, content)
        except ImportError:
            print("请先安装依赖：pip install selenium webdriver-manager")
            print("或者先复制内容，然后手动粘贴到公众号后台")


def cmd_image(article_index: int = None):
    """为文章生成配图"""
    from services.image_service import ImageService

    service = ArticleService()
    articles = service.list_articles()

    if not articles:
        print("没有可配图的文章")
        print("请先生成文章：python main.py search <关键词>")
        return

    # 如果没有指定编号，让用户选择
    if article_index is None:
        print("\n请选择要配图的文章编号：")
        for i, article in enumerate(articles[:10], 1):
            print(f"  {i}. {article['topic']}")
        print()
        try:
            choice = input("请输入编号: ")
            article_index = int(choice)
        except ValueError:
            print("无效编号")
            return

    index = article_index - 1
    if index < 0 or index >= len(articles):
        print(f"文章编号无效，请选择1-{len(articles)}之间的数字")
        return

    article = articles[index]
    print(f"\n正在为文章生成配图: {article['topic']}")

    # 生成配图
    image_service = ImageService()
    result = image_service.generate_for_article(article['filepath'])

    if result:
        print("=" * 50)
        print("配图生成成功！")
        print(f"图片路径: {result}")
        print("=" * 50)
    else:
        print("配图生成失败，请检查API配置")


def show_help():
    """显示帮助"""
    print("=" * 50)
    print("使用方法:")
    print("  search <关键词> 或 -s    - 搜索关键词生成文章（推荐）")
    print("  gen 或 -g             - 快速生成文章（热点+AI写作+复制）")
    print("  hot 或 -h              - 获取今日热点")
    print("  write <编号> 或 -w     - 选择话题写文章")
    print("  list 或 -l             - 查看历史文章")
    print("  copy <编号> 或 -c      - 复制历史文章")
    print("  image <编号> 或 -i     - 为文章生成配图")
    print("  publish <编号> 或 -p    - 发布到公众号草稿箱")
    print("  help 或 -h             - 查看帮助")
    print()
    print("示例:")
    print("  python main.py search 春节      # 搜索春节相关生成文章")
    print("  python main.py -s AI           # 搜索AI相关生成文章")
    print("  python main.py gen              # 快速生成文章")
    print("  python main.py hot              # 获取今日热点")
    print("  python main.py image 1          # 为第1篇文章生成配图")
    print("=" * 50)


def main():
    """主函数"""
    print_banner()

    # 检查依赖
    try:
        import pyperclip
    except ImportError:
        print("请先安装 pyperclip: pip install pyperclip")
        print()
        return

    # 解析命令行参数
    args = sys.argv[1:]

    if not args:
        show_help()
        return

    # 解析命令（去掉开头的/）
    cmd_str = args[0].lstrip("/")

    # 获取命令类型
    cmd_type = COMMANDS.get(cmd_str, None)

    if cmd_type is None:
        print(f"未知命令: {args[0]}")
        print("运行 help 查看可用命令")
        return

    # 处理不同命令
    if cmd_type == "hot":
        cmd_hot()

    elif cmd_type == "search":
        keyword = args[1] if len(args) > 1 else None
        cmd_search(keyword)

    elif cmd_type == "write":
        if len(args) > 1:
            try:
                index = int(args[1])
                cmd_write(index)
            except ValueError:
                print("请输入有效的编号")
        else:
            print("请指定话题编号，例如: /写文章 1")

    elif cmd_type == "list":
        cmd_list()

    elif cmd_type == "copy":
        if len(args) > 1:
            try:
                index = int(args[1])
                cmd_copy(index)
            except ValueError:
                print("请输入有效的编号")
        else:
            print("请指定文章编号，例如: copy 1")

    elif cmd_type == "gen":
        if len(args) > 1:
            try:
                index = int(args[1])
                cmd_gen(index)
            except ValueError:
                print("请输入有效的编号")
        else:
            cmd_gen()

    elif cmd_type == "publish":
        if len(args) > 1:
            try:
                index = int(args[1])
                cmd_publish(index)
            except ValueError:
                print("请输入有效的编号")
        else:
            cmd_publish()

    elif cmd_type == "image":
        if len(args) > 1:
            try:
                index = int(args[1])
                cmd_image(index)
            except ValueError:
                print("请输入有效的编号")
        else:
            cmd_image()

    elif cmd_type == "help":
        show_help()


if __name__ == "__main__":
    main()
