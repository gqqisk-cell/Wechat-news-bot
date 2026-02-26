import requests
from datetime import datetime

# ========== Configuration ==========
# Replace with your actual information
WECHAT_APPID = "wxfa348848aa8f4475"  # Replace with your appID
WECHAT_SECRET = "a782181ac5833bd2cf483856c8a9cfde"  # Replace with your appsecret
WECHAT_USERID = "oHh0G3Y5LKos7qEDyK-okZfGkpI0"  # Replace with your WeChatID

# ========== Data Fetching Functions ==========

def get_gold_price():
    """Get gold price in CNY per gram"""
    try:
        # Using MetalpriceAPI (free, no API key required)
        url = "https://api.metalpriceapi.com/v1/latest"
        response = requests.get(url)
        data = response.json()
        
        if data.get('success') and 'rates' in data:
            # Get gold price (USD per ounce)
            gold_usd_per_oz = data['rates']['USDXAU (Gold)']
            
            # Get exchange rate
            exchange_url = "https://api.exchangerate-api.com/v4/latest/USD"
            exchange_resp = requests.get(exchange_url)
            exchange_data = exchange_resp.json()
            usd_to_cny = exchange_data['rates']['CNY']
            
            # Calculate: USD/oz * rate / 31.1035 = CNY/gram
            gold_cny_per_gram = (gold_usd_per_oz * usd_to_cny) / 31.1035
            
            return f"Gold: CNY {gold_cny_per_gram:.2f}/gram"
        else:
            return "Gold: Data unavailable"
    except Exception as e:
        print(f"Failed to get gold price: {str(e)}")
        return "Gold: Failed"

def get_exchange_rates():
    """Get exchange rates (USD/CNY + CAD/USD)"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        
        usd_to_cny = data['rates']['CNY']
        cad_to_usd = data['rates']['CAD']
        
        return f"""Exchange Rates:
1 USD = {usd_to_cny:.4f} CNY
1 CAD = {cad_to_usd:.4f} USD"""
    except Exception as e:
        print(f"Failed to get exchange rates: {str(e)}")
        return "Exchange Rates: Failed"

def get_tech_news():
    """Get tech finance news (3 items)"""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'technology finance',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 3,
            'apiKey': 'demo'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            news_list = []
            for i, article in enumerate(data['articles'][:3], 1):
                title = article['title']
                url_link = article['url']
                # Truncate long titles
                if len(title) > 50:
                    title = title[:50] + "..."
                news_list.append(f"{i}. {title}\n   {url_link}")
            
            news_text = "\n\n".join(news_list)
        else:
            news_text = "No recent news available"
            
        return f"Tech Finance News:\n{news_text}"
    except Exception as e:
        print(f"Failed to get news: {str(e)}")
        return "Tech Finance News: Failed"

def get_wechat_access_token():
    """Get WeChat access token"""
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
        response = requests.get(url)
        data = response.json()
        
        if 'access_token' in data:
            return data['access_token']
        else:
            print(f"Failed to get access_token: {data}")
            return None
    except Exception as e:
        print(f"Exception getting access_token: {str(e)}")
        return None

def send_wechat_message(message):
    """Send WeChat message"""
    try:
        access_token = get_wechat_access_token()
        if not access_token:
            print("Cannot get access_token, send failed")
            return False
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        data = {
            "touser": WECHAT_USERID,
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        # Ensure UTF-8 encoding
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("Message sent successfully")
            return True
        else:
            print(f"Message send failed: {result}")
            return False
            
    except Exception as e:
        print(f"Exception sending message: {str(e)}")
        return False

# ========== Main Program ==========

def main():
    # Compose message content (English only, no emoji)
    today = datetime.now().strftime("%Y-%m-%d")
    
    message = f"""【{today} Finance Brief】

{get_gold_price()}

{get_exchange_rates()}

{get_tech_news()}

---
Auto Update | Mon/Wed/Fri 8:30 AM"""
    
    # Send message
    success = send_wechat_message(message)
    
    if success:
        print("Push complete!")
    else:
        print("Push failed, please check configuration")

if __name__ == "__main__":
    main()
