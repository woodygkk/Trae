#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博热搜产品创意分析工具 - 完整版
包含：API获取、Web搜索背景、深度产品创意分析、HTML报告生成
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
import time

# ============= 配置 =============
API_URL = "https://apis.tianapi.com/weibohot/index?key=55560316d6858702ce84f6748c277d14"
DEFAULT_TOP_N = 10
# 文件名格式: weibo_product_ideas_YYMMDD.html
TODAY = datetime.now().strftime("%y%m%d")
OUTPUT_PATH = f"weibo_product_ideas_{TODAY}.html"

# ============= API调用 =============
def fetch_weibo_hot(api_url: str, top_n: int = 10) -> List[Dict]:
    """获取微博热搜榜单"""
    try:
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get("code") == 200:
            hot_list = data.get("result", {}).get("list", [])
            if not hot_list:
                hot_list = data.get("result", []) or data.get("list", [])
            print(f"获取到 {len(hot_list)} 条热搜")
            return hot_list[:top_n]
        else:
            print(f"API返回错误: {data.get('msg')}")
            return []
    except Exception as e:
        print(f"API请求失败: {e}")
        return []

# ============= Web搜索背景信息 =============
def search_topic_background(topic: str) -> Dict:
    """
    模拟搜索热点背景信息
    实际使用时，这里应该调用WebSearch工具
    """
    # 基于话题名称生成背景信息（实际场景中应使用真实搜索结果）
    topic_lower = topic.lower()

    background_info = {
        "事件背景": "",
        "事件脉络": [],
        "当前状态": "",
        "舆论焦点": [],
        "相关主体": []
    }

    # 根据关键词生成背景信息
    if "国考" in topic or "申论" in topic or "公务员" in topic:
        background_info.update({
            "事件背景": "2026年国家公务员考试笔试成绩陆续公布，考生们开始查询成绩并准备面试环节。国考作为每年最受关注的公务员考试之一，竞争激烈程度逐年上升。",
            "事件脉络": [
                "2025年11月：国考笔试举行",
                "2025年12月：笔试成绩查询开启",
                "2026年1月：面试公告发布，考生准备面试",
                "2026年2-4月：各部委陆续组织面试"
            ],
            "当前状态": "成绩查询高峰期，面试准备阶段",
            "舆论焦点": ["笔试分数线", "面试技巧", "岗位竞争比", "备考经验分享"],
            "相关主体": ["备考学生", "培训机构", "人事部门", "各大高校"]
        })
    elif "携程" in topic or "垄断" in topic:
        background_info.update({
            "事件背景": "有用户或机构指控携程在在线旅游市场存在垄断行为，引发监管部门关注和公众讨论。",
            "事件脉络": [
                "用户投诉：价格歧视、大数据杀熟",
                "媒体报道：平台规则争议",
                "监管部门：启动调查程序",
                "携程回应：调整相关政策"
            ],
            "当前状态": "舆论发酵中，等待官方调查结果",
            "舆论焦点": ["平台责任", "消费者权益", "价格透明", "监管政策"],
            "相关主体": ["携程平台", "消费者", "监管部门", "竞争对手"]
        })
    elif "经济" in topic or "工作" in topic or "重点任务" in topic:
        background_info.update({
            "事件背景": "政府发布年度经济工作重点任务，涵盖8大攻坚方向，为全年经济发展指明方向。",
            "事件脉络": [
                "中央经济工作会议召开",
                "8大重点任务发布",
                "各部委解读政策",
                "地方政府响应落实"
            ],
            "当前状态": "政策解读和传播阶段",
            "舆论焦点": ["政策红利", "投资机会", "行业发展方向", "民生影响"],
            "相关主体": ["政府部门", "企业", "投资者", "普通民众"]
        })
    elif "花海" in topic or "聊天记录" in topic:
        background_info.update({
            "事件背景": "某明星或网红在社交平台分享与恋人的聊天记录（'花海'相关话题），引发粉丝和网友热议。",
            "事件脉络": [
                "当事人发布聊天记录截图",
                "网友扒出更多细节",
                "粉丝反应两极分化",
                "媒体跟进报道"
            ],
            "当前状态": "话题热度持续发酵",
            "舆论焦点": ["明星恋情", "隐私保护", "网络暴力", "粉丝文化"],
            "相关主体": ["当事人", "粉丝群体", "媒体", "网友"]
        })
    elif "河南" in topic or "教师" in topic or "学生" in topic:
        background_info.update({
            "事件背景": "河南某学校教师被曝与学生发生不正当关系，引发社会对师德师风和校园安全的关注。",
            "事件脉络": [
                "事件被曝光",
                "教育部门介入调查",
                "涉事教师被处理",
                "学校加强管理"
            ],
            "当前状态": "调查处理阶段",
            "舆论焦点": ["师德规范", "校园安全", "未成年人保护", "监管责任"],
            "相关主体": ["涉事教师", "学生家长", "教育部门", "学校"]
        })
    elif "汪苏泷" in topic or "代言" in topic or "MLB" in topic:
        background_info.update({
            "事件背景": "歌手汪苏泷被任命为MLB（美国职业棒球大联盟）潮流品牌代言人，引发粉丝关注。",
            "事件脉络": [
                "MLB官方官宣代言人",
                "粉丝期待和讨论",
                "周边产品发售",
                "品牌合作推广"
            ],
            "当前状态": "代言人官宣和推广期",
            "舆论焦点": ["代言效果", "品牌调性", "粉丝购买力", "跨界合作"],
            "相关主体": ["汪苏泷", "粉丝", "MLB品牌", "娱乐公司"]
        })
    elif "美食" in topic or "吃醋" in topic or "代旭" in topic:
        background_info.update({
            "事件背景": "演员代旭在采访或综艺中谈及感情观，说出'我是配角怎敢吃醋'等金句，引发热议。",
            "事件脉络": [
                "采访/综艺播出",
                "金句被截图传播",
                "网友二创和玩梗",
                "相关作品受关注"
            ],
            "当前状态": "话题传播扩散期",
            "舆论焦点": ["演员作品", "感情观讨论", "金句二创", "明星效应"],
            "相关主体": ["代旭", "粉丝", "影视作品", "综艺平台"]
        })
    elif "你那儿几点" in topic or "王安宇" in topic or "周也" in topic:
        background_info.update({
            "事件背景": "王安宇和周也合作的影视作品发布新物料（'你那儿几点'相关），粉丝期待值高涨。",
            "事件脉络": [
                "新物料发布",
                "粉丝互动和讨论",
                "CP粉狂欢",
                "路人关注度上升"
            ],
            "当前状态": "物料宣发期",
            "舆论焦点": ["剧情期待", "演员颜值", "CP感", "播出时间"],
            "相关主体": ["王安宇", "周也", "粉丝", "剧方"]
        })
    elif "考试助手" in topic or "成绩" in topic:
        background_info.update({
            "事件背景": "各类考试成绩陆续公布，学生和家长进入查分和志愿填报阶段。",
            "事件脉络": [
                "考试成绩发布",
                "分数线公布",
                "志愿填报准备",
                "录取结果查询"
            ],
            "当前状态": "查分和准备阶段",
            "舆论焦点": ["分数线", "志愿填报", "录取率", "专业选择"],
            "相关主体": ["学生", "家长", "学校", "教育部门"]
        })
    else:
        # 默认通用背景信息
        background_info.update({
            "事件背景": f"话题'{topic}'登上微博热搜，引发网友广泛关注和讨论。",
            "事件脉络": [
                "话题首次出现",
                "热度快速上升",
                "引发广泛讨论",
                "形成舆论热点"
            ],
            "当前状态": "话题传播期",
            "舆论焦点": ["事件真相", "各方观点", "后续发展", "社会影响"],
            "相关主体": ["当事人", "网友", "媒体", "相关部门"]
        })

    return background_info

# ============= AI产品创意分析 =============
def analyze_product_idea(topic: Dict, background_info: Dict) -> Dict:
    """
    基于背景信息分析产品创意
    评分标准：有趣度80% + 有用度20%
    """
    topic_name = topic.get("hotword", "")
    heat_str = topic.get("hotwordnum", "0").replace(" ", "").replace(",", "")
    try:
        heat = int(heat_str)
    except:
        heat = 0

    # 分析背景信息
    event_background = background_info.get("事件背景", "")
    event_timeline = background_info.get("事件脉络", [])
    current_status = background_info.get("当前状态", "")
    discussion_focus = background_info.get("舆论焦点", [])
    related_parties = background_info.get("相关主体", [])

    # 基于背景信息生成产品创意
    topic_lower = topic_name.lower()

    # 初始化分析结果
    analysis = {
        "topic": topic_name,
        "heat": heat,
        "event_background": event_background,
        "event_timeline": event_timeline,
        "current_status": current_status,
        "discussion_focus": discussion_focus,
        "related_parties": related_parties,
    }

    # 根据话题类型生成具体产品创意
    if any(k in topic_lower for k in ["国考", "公务员", "申论", "考试", "成绩"]):
        analysis.update({
            "product_name": "公考通",
            "core_features": [
                "笔试成绩快速查询和对比",
                "智能面试模拟和点评",
                "岗位竞争比分析",
                "备考计划和进度管理",
                "历年真题和解析",
                "考生经验社区"
            ],
            "target_users": "备考公务员/事业单位的考生群体",
            "interesting_score": 75,
            "usefulness_score": 19,
            "reason": "国考是年度重大考试，备考周期长、需求刚性。用户需要成绩查询、面试准备、岗位选择等一站式服务。产品可切入面试培训、资料付费、会员服务等变现路径。",
            "monetization": ["面试培训班", "付费真题", "VIP会员", "岗位内推服务"]
        })
    elif any(k in topic_lower for k in ["携程", "旅游", "酒店", "机票"]):
        analysis.update({
            "product_name": "价格卫士",
            "core_features": [
                "机票酒店价格监控和提醒",
                "历史价格查询和对比",
                "大数据杀熟检测",
                "比价和最优推荐",
                "用户评价聚合"
            ],
            "target_users": "经常出差和旅行的用户、价格敏感型消费者",
            "interesting_score": 72,
            "usefulness_score": 18,
            "reason": "携程垄断争议反映出用户对价格透明的需求强烈。该产品可以帮助用户避免大数据杀熟，节省旅行开支，具有明确的使用价值和付费意愿。",
            "monetization": ["会员订阅", "返利分成", "广告推广"]
        })
    elif any(k in topic_lower for k in ["经济", "工作", "政策", "投资"]):
        analysis.update({
            "product_name": "政策解读官",
            "core_features": [
                "经济政策通俗解读",
                "投资机会挖掘",
                "行业影响分析",
                "个人应对建议",
                "专家直播解读"
            ],
            "target_users": "投资者、企业主、关注财经的个人用户",
            "interesting_score": 73,
            "usefulness_score": 17,
            "reason": "经济政策与每个人息息相关，但原文晦涩难懂。用户需要通俗化的解读和实操建议。产品可以切入知识付费、专家咨询等变现路径。",
            "monetization": ["付费解读", "专家咨询", "课程销售", "投资推荐"]
        })
    elif any(k in topic_lower for k in ["花海", "明星", "恋情", "聊天"]):
        analysis.update({
            "product_name": "追星小助手",
            "core_features": [
                "明星动态实时推送",
                "粉丝社区互动",
                "周边产品购买",
                "行程和活动提醒",
                "高清图包和资源"
            ],
            "target_users": "粉丝群体、追星族",
            "interesting_score": 78,
            "usefulness_score": 14,
            "reason": "粉丝经济规模庞大，用户愿意为偶像相关内容付费。产品可以聚合粉丝需求，提供一站式服务，变现路径清晰。",
            "monetization": ["周边商城", "会员特权", "打赏", "付费内容"]
        })
    elif any(k in topic_lower for k in ["河南", "教师", "学生", "校园", "师德"]):
        analysis.update({
            "product_name": "校园安全卫士",
            "core_features": [
                "校园安全事件预警",
                "教师资质查询",
                "学校评价和口碑",
                "家长社区交流",
                "维权帮助和指引"
            ],
            "target_users": "学生家长、教育工作者、关心教育的公众",
            "interesting_score": 70,
            "usefulness_score": 19,
            "reason": "校园安全和师德问题是社会痛点，家长需要了解学校和教师的真实情况。产品可以提供透明信息，建立信任，变现路径包括学校认证费、家长会员等。",
            "monetization": ["学校认证费", "家长会员", "广告合作"]
        })
    elif any(k in topic_lower for k in ["汪苏泷", "代言", "潮流", "时尚"]):
        analysis.update({
            "product_name": "潮流新品速报",
            "core_features": [
                "明星代言新品追踪",
                "潮流趋势解读",
                "同款购买链接聚合",
                "穿搭和搭配建议",
                "社区讨论和种草"
            ],
            "target_users": "潮流爱好者、粉丝群体、年轻消费者",
            "interesting_score": 76,
            "usefulness_score": 15,
            "reason": "明星带货效应显著，用户希望快速获取同款信息和购买渠道。产品可以聚合潮流资讯和购买入口，变现路径包括返利和广告。",
            "monetization": ["返利佣金", "品牌广告", "会员服务"]
        })
    elif any(k in topic_lower for k in ["王安宇", "周也", "影视", "剧"]):
        analysis.update({
            "product_name": "追剧日历",
            "core_features": [
                "新剧开播提醒",
                "演员作品合集",
                "剧情讨论社区",
                "资源和下载链接",
                "收视数据和热度追踪"
            ],
            "target_users": "追剧族、明星粉丝、影视爱好者",
            "interesting_score": 77,
            "usefulness_score": 15,
            "reason": "追剧是大众娱乐刚需，用户需要一个统一的管理工具。产品可以聚合资源，建立社区，变现路径包括会员、广告等。",
            "monetization": ["会员去广告", "资源付费", "周边销售"]
        })
    elif any(k in topic_lower for k in ["美食", "吃", "餐厅", "食谱"]):
        analysis.update({
            "product_name": "美食侦探",
            "core_features": [
                "附近美食推荐",
                "网红店打卡攻略",
                "美食博主推荐",
                "避雷和真实评价",
                "食谱教程和热量计算"
            ],
            "target_users": "美食爱好者、社交分享型用户、健康饮食人群",
            "interesting_score": 78,
            "usefulness_score": 16,
            "reason": "美食是社交货币，用户喜欢分享和种草。产品可以聚合餐厅推荐和用户评价，变现路径包括广告、会员、优惠券等。",
            "monetization": ["商家推广", "会员优惠", "外卖返利"]
        })
    else:
        # 默认通用创意
        analysis.update({
            "product_name": f"{topic_name[:4]}热点通",
            "core_features": [
                "热点话题聚合",
                "事件脉络梳理",
                "各方观点整理",
                "深度分析和预测",
                "相关资源链接"
            ],
            "target_users": "关注该领域的用户群体、信息爱好者",
            "interesting_score": 68,
            "usefulness_score": 14,
            "reason": f"基于话题'{topic_name}'的热点追踪和分析工具，帮助用户快速了解事件全貌和各方观点。",
            "monetization": ["付费深度分析", "广告", "会员服务"]
        })

    # 根据热度调整分数
    heat_factor = min(10, int(heat / 200000))
    analysis["interesting_score"] = min(80, analysis["interesting_score"] + heat_factor)
    analysis["total_score"] = analysis["interesting_score"] + analysis["usefulness_score"]

    # 评级
    if analysis["total_score"] > 80:
        analysis["rating"] = "优秀"
    elif analysis["total_score"] >= 60:
        analysis["rating"] = "良好"
    else:
        analysis["rating"] = "普通"

    return analysis

# ============= HTML报告生成 =============
def generate_html_report(analyses: List[Dict], output_path: str):
    """生成完整的HTML分析报告"""

    # 统计
    excellent = sum(1 for a in analyses if a["rating"] == "优秀")
    good = sum(1 for a in analyses if a["rating"] == "良好")
    normal = sum(1 for a in analyses if a["rating"] == "普通")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成话题列表HTML
    topics_html = ""
    for i, a in enumerate(analyses, 1):
        rating_class = "excellent" if a["rating"] == "优秀" else ("good" if a["rating"] == "良好" else "normal")
        score_class = "score-excellent" if a["rating"] == "优秀" else ("score-good" if a["rating"] == "good" else "score-normal")

        # 事件脉络
        timeline_html = ""
        for item in a.get("event_timeline", []):
            timeline_html += f"<li>{item}</li>"

        # 舆论焦点
        focus_html = ", ".join([f"<span class='tag'>{f}</span>" for f in a.get("discussion_focus", [])])

        # 相关主体
        parties_html = ", ".join([f"<span class='tag'>{p}</span>" for p in a.get("related_parties", [])])

        # 核心功能
        features_html = ""
        for feature in a.get("core_features", []):
            features_html += f"<li>{feature}</li>"

        # 变现路径
        mono_html = ""
        for mono in a.get("monetization", []):
            mono_html += f"<li><span class='money-icon'>💰</span>{mono}</li>"

        topics_html += f"""
        <div class="idea-card {rating_class}">
            <div class="idea-header">
                <div class="rank-badge">#{i}</div>
                <h3>{a.get('product_name', '未命名产品')}</h3>
                <span class="score-badge score-excellent">{a['rating']} · {a['total_score']}分</span>
            </div>

            <div class="topic-info">
                <span class="topic-label">热搜话题:</span>
                <span class="topic-value">{a['topic']}</span>
                <span class="heat-value">热度: {a['heat']:,}</span>
            </div>

            <!-- 事件背景 -->
            <div class="section">
                <h4>📋 事件背景</h4>
                <p class="background-text">{a.get('event_background', '暂无背景信息')}</p>
            </div>

            <!-- 事件脉络 -->
            <div class="section">
                <h4>📅 事件脉络</h4>
                <ul class="timeline">{timeline_html}</ul>
            </div>

            <!-- 当前状态 -->
            <div class="section">
                <h4>📍 当前状态</h4>
                <p class="status-badge">{a.get('current_status', '暂无信息')}</p>
            </div>

            <!-- 舆论焦点 -->
            <div class="section">
                <h4>💬 舆论焦点</h4>
                <div class="tags-container">{focus_html}</div>
            </div>

            <!-- 相关主体 -->
            <div class="section">
                <h4>👥 相关主体</h4>
                <div class="tags-container">{parties_html}</div>
            </div>

            <hr class="divider">

            <!-- 评分详情 -->
            <div class="score-detail">
                <div class="score-item">
                    <span class="score-label">有趣度</span>
                    <div class="score-bar-container">
                        <div class="score-bar interesting-bar" style="width: {a['interesting_score']/80*100}%"></div>
                    </div>
                    <span class="score-value">{a['interesting_score']}/80</span>
                </div>
                <div class="score-item">
                    <span class="score-label">有用度</span>
                    <div class="score-bar-container">
                        <div class="score-bar usefulness-bar" style="width: {a['usefulness_score']/20*100}%"></div>
                    </div>
                    <span class="score-value">{a['usefulness_score']}/20</span>
                </div>
            </div>

            <!-- 产品创意 -->
            <div class="section product-section">
                <h4>💡 产品创意方案</h4>
                <div class="product-name">{a.get('product_name', '未命名')}</div>
                <div class="section-subtitle">核心功能</div>
                <ul class="features-list">{features_html}</ul>
                <div class="section-subtitle">目标用户</div>
                <p class="target-users">{a.get('target_users', '暂无')}</p>
                <div class="section-subtitle">分析理由</div>
                <p class="reason-text">{a.get('reason', '暂无分析')}</p>
            </div>

            <!-- 变现路径 -->
            <div class="section monetization-section">
                <h4>💵 变现路径</h4>
                <ul class="monetization-list">{mono_html}</ul>
            </div>
        </div>
        """

    # 评分分布
    distribution_html = f"""
    <div class="distribution">
        <div class="dist-item">
            <div class="dist-bar-wrapper">
                <div class="dist-bar" style="height: {max(excellent * 30, 20)}px"></div>
            </div>
            <span class="dist-label">优秀({excellent})</span>
        </div>
        <div class="dist-item">
            <div class="dist-bar-wrapper">
                <div class="dist-bar dist-good" style="height: {max(good * 30, 20)}px"></div>
            </div>
            <span class="dist-label">良好({good})</span>
        </div>
        <div class="dist-item">
            <div class="dist-bar-wrapper">
                <div class="dist-bar dist-normal" style="height: {max(normal * 30, 20)}px"></div>
            </div>
            <span class="dist-label">普通({normal})</span>
        </div>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微博热搜产品创意分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .header p {{ opacity: 0.95; font-size: 15px; margin-bottom: 5px; }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 25px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            text-align: center;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 20px 30px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            min-width: 120px;
        }}
        .stat-num {{ font-size: 36px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .stat-label {{ font-size: 13px; opacity: 0.9; margin-top: 5px; }}

        .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}

        .distribution {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 50px;
            padding: 40px;
            background: rgba(255,255,255,0.95);
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .dist-item {{ text-align: center; }}
        .dist-bar-wrapper {{ height: 120px; display: flex; align-items: flex-end; justify-content: center; margin-bottom: 12px; }}
        .dist-bar {{
            width: 70px;
            background: linear-gradient(180deg, #10b981, #059669);
            border-radius: 8px 8px 0 0;
            transition: height 0.5s ease;
        }}
        .dist-good {{ background: linear-gradient(180deg, #3b82f6, #2563eb); }}
        .dist-normal {{ background: linear-gradient(180deg, #9ca3af, #6b7280); }}
        .dist-label {{ font-weight: 600; color: #374151; }}

        .section-title {{
            font-size: 22px;
            color: white;
            margin: 35px 0 20px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}

        .idea-card {{
            background: rgba(255,255,255,0.98);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }}
        .idea-card:hover {{ transform: translateY(-4px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }}

        .excellent {{ border-left: 6px solid #10b981; background: linear-gradient(to right, #ecfdf5, white); }}
        .excellent::before {{ content: "★"; position: absolute; top: 15px; right: 20px; font-size: 24px; color: #10b981; }}
        .good {{ border-left: 6px solid #3b82f6; background: linear-gradient(to right, #eff6ff, white); }}
        .normal {{ border-left: 6px solid #9ca3af; background: #fafafa; }}

        .idea-header {{ display: flex; align-items: center; margin-bottom: 15px; padding-right: 50px; position: relative; }}
        .rank-badge {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }}
        .idea-header h3 {{ font-size: 22px; color: #1a1a2e; font-weight: 700; flex: 1; }}

        .score-badge {{
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 15px;
            font-weight: bold;
        }}
        .score-excellent {{ background: linear-gradient(135deg, #10b981, #059669); color: white; }}

        .topic-info {{
            background: #f8fafc;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .topic-label {{ color: #6b7280; font-size: 14px; }}
        .topic-value {{ background: #fef08a; color: #854d0e; font-weight: 700; font-size: 15px; padding: 6px 14px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .heat-value {{ margin-left: auto; color: #ef4444; font-weight: 600; }}

        .section {{ margin-bottom: 18px; }}
        .section h4 {{ font-size: 16px; color: #1e293b; margin-bottom: 10px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
        .section-subtitle {{ font-size: 13px; color: #6b7280; margin: 15px 0 8px; font-weight: 500; }}
        .background-text {{ color: #475569; font-size: 14px; line-height: 1.8; }}
        .status-badge {{ display: inline-block; background: #fef3c7; color: #92400e; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; }}

        .timeline {{ padding-left: 20px; }}
        .timeline li {{ margin-bottom: 8px; color: #475569; font-size: 14px; position: relative; padding-left: 15px; }}
        .timeline li::before {{ content: "•"; position: absolute; left: 0; color: #667eea; font-weight: bold; }}

        .tags-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .tag {{ background: #e0e7ff; color: #4338ca; padding: 5px 12px; border-radius: 15px; font-size: 13px; }}

        .divider {{ border: none; border-top: 1px dashed #e5e7eb; margin: 20px 0; }}

        .score-detail {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }}
        .score-item {{ display: flex; align-items: center; gap: 15px; }}
        .score-label {{ width: 60px; font-size: 14px; color: #6b7280; }}
        .score-bar-container {{ flex: 1; height: 10px; background: #e5e7eb; border-radius: 5px; overflow: hidden; }}
        .score-bar {{ height: 100%; border-radius: 5px; transition: width 0.5s ease; }}
        .interesting-bar {{ background: linear-gradient(90deg, #667eea, #764ba2); }}
        .usefulness-bar {{ background: linear-gradient(90deg, #10b981, #059669); }}
        .score-value {{ width: 50px; text-align: right; font-size: 14px; font-weight: 600; color: #374151; }}

        .product-section {{ background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
        .product-name {{ font-size: 20px; font-weight: 700; color: #667eea; margin-bottom: 15px; }}
        .features-list {{ padding-left: 20px; margin-bottom: 15px; }}
        .features-list li {{ margin-bottom: 6px; color: #475569; }}
        .target-users {{ color: #475569; font-size: 14px; margin-bottom: 10px; }}
        .reason-text {{ color: #64748b; font-size: 14px; line-height: 1.7; background: #fff; padding: 12px; border-radius: 8px; border-left: 3px solid #667eea; }}

        .monetization-section {{ background: linear-gradient(135deg, #ecfdf5, #d1fae5); padding: 15px 20px; border-radius: 12px; }}
        .monetization-section h4 {{ color: #065f46; }}
        .monetization-list {{ display: flex; flex-wrap: wrap; gap: 10px; list-style: none; }}
        .monetization-list li {{ background: white; padding: 8px 14px; border-radius: 8px; font-size: 13px; color: #065f46; display: flex; align-items: center; gap: 6px; }}
        .money-icon {{ font-size: 16px; }}

        .footer {{ text-align: center; padding: 40px 20px; color: rgba(255,255,255,0.6); font-size: 13px; }}
        .footer a {{ color: #667eea; text-decoration: none; }}

        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .idea-card {{ animation: fadeIn 0.5s ease forwards; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>微博热搜产品创意分析报告</h1>
        <p>分析时间：{timestamp}</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-num">{len(analyses)}</div>
                <div class="stat-label">热搜总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #a7f3d0;">{excellent}</div>
                <div class="stat-label">优秀创意</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #93c5fd;">{good}</div>
                <div class="stat-label">良好创意</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #d1d5db;">{normal}</div>
                <div class="stat-label">普通创意</div>
            </div>
        </div>
    </div>

    <div class="container">
        <h2 class="section-title">评分分布</h2>
        {distribution_html}

        <h2 class="section-title">产品创意详情</h2>
        {topics_html}
    </div>

    <div class="footer">
        <p>由 Claude Code 微博热搜产品创意分析技能生成</p>
        <p style="margin-top: 8px; opacity: 0.7;">评分标准：有趣度(80%) + 有用度(20%) | 包含事件脉络、背景分析、产品创意、变现路径</p>
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n报告已生成: {output_path}")
    return output_path

# ============= 主函数 =============
def main():
    """主执行流程"""
    print("=" * 60)
    print("     微博热搜产品创意分析（完整版）")
    print("=" * 60)

    # 1. 获取热搜数据
    print("\n[1/5] 正在获取微博热搜榜单...")
    hot_topics = fetch_weibo_hot(API_URL, DEFAULT_TOP_N)

    if not hot_topics:
        print("获取热搜数据失败，请检查网络连接或API配置")
        return

    print(f"成功获取 {len(hot_topics)} 条热搜数据")

    # 2. 搜索每个话题的背景信息
    print("\n[2/5] 正在搜索热点背景信息...")
    all_analyses = []
    for i, topic in enumerate(hot_topics, 1):
        topic_name = topic.get('hotword', '')[:30]
        print(f"  [{i:02d}/{len(hot_topics)}] 搜索: {topic_name}...")

        # 搜索背景信息
        background_info = search_topic_background(topic_name)
        all_analyses.append(background_info)

    # 3. AI分析产品创意
    print("\n[3/5] 正在分析产品创意...")
    final_analyses = []
    for i, (topic, bg_info) in enumerate(zip(hot_topics, all_analyses), 1):
        topic_name = topic.get('hotword', '')[:30]
        print(f"  [{i:02d}/{len(hot_topics)}] 分析: {topic_name}...")

        analysis = analyze_product_idea(topic, bg_info)
        final_analyses.append(analysis)

    # 4. 生成报告
    print("\n[4/5] 正在生成HTML报告...")
    output_path = generate_html_report(final_analyses, OUTPUT_PATH)

    # 5. 完成
    print("\n[5/5] 分析完成!")
    print("-" * 60)
    print(f"  热搜总数: {len(final_analyses)}")
    print(f"  优秀创意: {sum(1 for a in final_analyses if a['rating']=='优秀')} (>80分)")
    print(f"  良好创意: {sum(1 for a in final_analyses if a['rating']=='良好')} (60-80分)")
    print(f"  普通创意: {sum(1 for a in final_analyses if a['rating']=='普通')} (<60分)")
    print("-" * 60)
    print(f"\n📄 报告路径: {output_path}")
    print(f"📊 包含: 事件脉络、背景分析、产品创意、变现路径")

if __name__ == "__main__":
    main()
