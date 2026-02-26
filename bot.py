import requests
from datetime import datetime

# ========== Configuration ==========
# Replace with your actual information
WECHAT_APPID = "wxfa348848aa8f4475"  # Replace with your appID
WECHAT_SECRET = "a782181ac5833bd2cf483856c8a9cfde"  # Replace with your appsecret
WECHAT_USERID = "oHh0G3Y5LKos7qEDyK-okZfGkpI0"  # Replace with your WeChatID

# ========== Data Fetching Functions ==========

def get_gold_price():
    """Get gold price in CNY per gram using MetalpriceAPI"""
    try:
        # MetalpriceAPI (Free tier available, no API key required for basic usage)
        url = "https://api.metalpriceapi.com/v1/latest?base=USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('success') and 'rates' in data:
            # Get gold price in USD per ounce
            gold_usd_per_oz = data['rates']['USDXAU (Gold)']
            
            # Get USD to CNY exchange rate from the same API
            usd_to_cny = data['rates']['CNY']
            
            # Convert to CNY per gram (1 ounce = 31.1035 grams)
            gold_cny_per_gram = (gold_usd_per_oz * usd_to_cny) / 31.1035
            
            return f"Gold: CNY {gold_cny_per_gram:.2f}/gram"
        else:
            return "Gold: Data unavailable"
    except Exception as e:
        print(f"Failed to get gold price: {str(e)}")
        return "Gold: Data unavailable"

def get_exchange_rates():
    """Get exchange rates (USD/CNY + CAD/USD)"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'rates' in data:
            usd_to_cny = data['rates']['CNY']
            cad_to_usd = data['rates']['CAD']
            
            return f"""Exchange Rates:
1 USD = {usd_to_cny:.4f} CNY
1 CAD = {cad_to_usd:.4f} USD"""
        else:
            return "Exchange Rates: Data unavailable"
    except Exception as e:
        print(f"Failed to get exchange rates: {str(e)}")
        return "Exchange Rates: Failed"

def get_wechat_access_token():
    """Get WeChat access token"""
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
        response = requests.get(url, timeout=10)
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
        response = requests.post(url, json=data, headers=headers, timeout=10)
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
    
    message = f"""[{today} Finance Brief]

{get_gold_price()}

{get_exchange_rates()}

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
