import requests
import json
from datetime import datetime

# ========== 配置区域 ==========
WECHAT_APPID = "你的appID"
WECHAT_SECRET = "你的appsecret"  
WECHAT_USERID = "你的WeChatID"

# ========== 数据获取函数 ==========

def get_gold_price():
    """获取黄金价格（人民币/克）"""
    try:
        # 使用免费API获取XAU价格
        url = "https://api.metals.live/v1/spot/gold"
        response = requests.get(url)
        data = response.json()
        
        # API返回的是美元/盎司，需要转换为人民币/克
        # 1盎司 = 31.1035克
        gold_usd_per_oz = data['price']
        
        # 获取当前汇率
        exchange_url = "https://api.exchangerate-api.com/v4/latest/USD"
        exchange_resp = requests.get(exchange_url)
        exchange_data = exchange_resp.json()
        usd_to_cny = exchange_data['rates']['CNY']
        
        # 计算：美元/盎司 × 汇率 ÷ 31.1035 = 人民币/克
        gold_cny_per_gram = (gold_usd_per_oz * usd_to_cny) / 31.1035
        
        return f"🥇 黄金价格：¥{gold_cny_per_gram:.2f}/克"
    except Exception as e:
        return f"🥇 黄金价格：获取失败 ({str(e)})"

def get_exchange_rates():
    """获取汇率信息"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        
        usd_to_cny = data['rates']['CNY']
        cad_to_usd = data['rates']['CAD']
        
        return f"""💱 汇率速报：
• 1 USD = {usd_to_cny:.4f} CNY
• 1 CAD = {cad_to_usd:.4f} USD"""
    except Exception as e:
        return f"💱 汇率：获取失败 ({str(e)})"

def get_tech_news():
    """获取科技金融新闻"""
    try:
        # 使用NewsAPI的免费端点（注意：这个API可能有调用限制）
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'technology finance',
            'language': 'zh',
            'sortBy': 'publishedAt',
            'pageSize': 3,
            'apiKey': 'demo'  # 使用demo key，实际使用时需要申请
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            news_list = []
            for article in data['articles'][:3]:
                title = article['title']
                url_link = article['url']
                news_list.append(f"• {title}\n  {url_link}")
            
            news_text = "\n\n".join(news_list)
        else:
            news_text = "暂无最新新闻"
            
        return f"📰 科技金融热点\n{news_text}"
    except Exception as e:
        return f"📰 新闻：获取失败 ({str(e)})"

def get_wechat_access_token():
    """获取微信access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
    response = requests.get(url)
    data = response.json()
    return data.get('access_token')

def send_wechat_message(message):
    """发送微信消息"""
    try:
        access_token = get_wechat_access_token()
        if not access_token:
            print("获取access_token失败")
            return False
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        data = {
            "touser": WECHAT_USERID,
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("消息发送成功")
            return True
        else:
            print(f"消息发送失败: {result}")
            return False
            
    except Exception as e:
        print(f"发送消息异常: {str(e)}")
        return False

# ========== 主程序 ==========

def main():
    # 组合消息内容
    today = datetime.now().strftime("%Y年%m月%d日 %A")
    
    message = f"""📅 {today}
════════════════════

{get_gold_price()}

{get_exchange_rates()}

{get_tech_news()}

════════════════════
⏰ 更新时间：{datetime.now().strftime("%H:%M")}
🤖 自动推送机器人"""
    
    # 发送消息
    send_wechat_message(message)
    
    print("推送完成！")

if __name__ == "__main__":
    main()
