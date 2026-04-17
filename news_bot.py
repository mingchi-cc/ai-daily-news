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
            "query": "AI OR artificial intelligence",
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
    content = f"【AI 每日简报】{beijing_time}\n\n"
    for i, news in enumerate(news_list, 1):
        content += f"{i}. {news['title']} → {news['url']}\n"
    
    payload = {"msg_type": "text", "content": {"text": content}}
    response = requests.post(webhook_url, json=payload)
    print("推送结果:", response.status_code, response.text)

if __name__ == "__main__":
    import os
    webhook = os.getenv("FEISHU_WEBHOOK")
    if not webhook:
        print("错误：未设置 FEISHU_WEBHOOK 环境变量")
        exit(1)
    
    news = fetch_hn_ai_news()
    send_to_feishu(news, webhook)
