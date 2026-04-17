import requests
import json
from datetime import datetime, timezone, timedelta

# 获取北京时间
beijing_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

def fetch_hn_ai_news():
    """从 Hacker News 搜索 AI 相关新闻"""
    try:
        # Hacker News 官方 API
        search_url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": "AI OR LLM OR GPT OR Claude OR \"machine learning\"",
            "tags": "story",
            "numericFilters": "created_at_i>{}".format(
                int((datetime.now() - timedelta(days=1)).timestamp())
            )
        }
        res = requests.get(search_url, params=params, timeout=10)
        data = res.json()
        news = []
        for hit in data.get("hits", [])[:5]:  # 取前5条
            title = hit.get("title", "")
            url = hit.get("url", f"https://news.ycombinator.com/item?id={hit['objectID']}")
            if title:
                news.append({"title": title, "url": url})
        return news
    except Exception as e:
        print(f"抓取失败: {e}")
        return [{"title": "今日暂无AI新闻", "url": "https://news.ycombinator.com"}]

def send_to_feishu(news_list, webhook_url):
    """发送消息到飞书"""
    def send_to_feishu(news, webhook_url):
    if not news or all("暂无" in item["title"] for item in news):
        # 强制保证至少一条消息
        news = [{"title": "🤖 今日 Hacker News 暂无 AI 相关新闻", "url": "https://news.ycombinator.com"}]
    
    elements = []
    for item in news[:5]:  # 最多5条
        elements.append({
            "tag": "div",
            "text": {
                "content": f"[{item['title']}]({item['url']})",
                "tag": "lark_md"
            }
        })
    
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"content": "🔥 每日AI新闻速递", "tag": "plain_text"}},
            "elements": elements
        }
    }
    
    resp = requests.post(webhook_url, json=card)
    print(f"推送结果: {resp.status_code} {resp.text}")  # 关键！打印响应
