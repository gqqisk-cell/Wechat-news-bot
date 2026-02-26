# -*- coding: utf-8 -*-
import requests
from datetime import datetime

# ========== 配置区域 ==========
# 请在这里填入你的真实信息
WECHAT_APPID = "wxfa348848aa8f4475"  # 替换成你的appID
WECHAT_SECRET = "a782181ac5833bd2cf483856c8a9cfde"  # 替换成你的appsecret
WECHAT_USERID = "oHh0G3Y5LKos7qEDyK-okZfGkpI0"  # 替换成你的WeChatID

# ========== 数据获取函数 ==========

def get_gold_price():
    """获取黄金价格（人民币/克）"""
    try:
        # 使用MetalpriceAPI（免费，无需API Key）
        url = "https://api.metalpriceapi.com/v1/latest"
        response = requests.get(url)
        data = response.json()
        
        if data.get('success') and 'rates' in data:
            # 获取黄金价格（美元/盎司）
            # API返回的是 "USDXAU (Gold)": 价格
            gold_usd_per_oz = data['rates']['USDXAU (Gold)']
            
            # 获取汇率
            exchange_url = "https://api.exchangerate-api.com/v4/latest/USD"
            exchange_resp = requests.get(exchange_url)
            exchange_data = exchange_resp.json()
            usd_to_cny = exchange_data['rates']['CNY']
            
            # 计算：美元/盎司 × 汇率 ÷ 31.1035 = 人民币/克
            gold_cny_per_gram = (gold_usd_per_oz * usd_to_cny) / 31.1035
            
            return f"黄金: {gold_cny_per_gram:.2f}元/克"
        else:
            return "黄金: 数据获取失败"
    except Exception as e:
        print(f"获取黄金价格失败: {str(e)}")
        return "黄金: 获取失败"

def get_exchange_rates():
    """获取汇率信息（美元兑人民币 + 加元兑美元）"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        
        usd_to_cny = data['rates']['CNY']
        cad_to_usd = data['rates']['CAD']
        
        return f"""汇率:
1美元 = {usd_to_cny:.4f}人民币
1加元 = {cad_to_usd:.4f}美元"""
    except Exception as e:
        print(f"获取汇率失败: {str(e)}")
        return "汇率: 获取失败"

def get_tech_news():
    """获取科技金融新闻（3条）"""
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
                # 简化标题，去掉多余内容
                if len(title) > 50:
                    title = title[:50] + "..."
                news_list.append(f"{i}. {title}\n   {url_link}")
            
            news_text = "\n\n".join(news_list)
        else:
            news_text = "暂无最新新闻"
            
        return f"科技金融热点:\n{news_text}"
    except Exception as e:
        print(f"获取新闻失败: {str(e)}")
        return "科技金融热点: 获取失败"

def get_wechat_access_token():
    """获取微信access_token"""
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
        response = requests.get(url)
        data = response.json()
        
        if 'access_token' in data:
            return data['access_token']
        else:
            print(f"获取access_token失败: {data}")
            return None
    except Exception as e:
        print(f"获取access_token异常: {str(e)}")
        return None

def send_wechat_message(message):
    """发送微信消息"""
    try:
        access_token = get_wechat_access_token()
        if not access_token:
            print("无法获取access_token，发送失败")
            return False
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        data = {
            "touser": WECHAT_USERID,
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        # 确保使用UTF-8编码
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(url, json=data, headers=headers)
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
    # 组合消息内容（纯中文，不使用emoji）
    today = datetime.now().strftime("%Y年%m月%d日")
    
    message = f"""【{today} 财经早报】

{get_gold_price()}

{get_exchange_rates()}

{get_tech_news()}

---
自动更新 | 每周一三五 8:30"""
    
    # 发送消息
    success = send_wechat_message(message)
    
    if success:
        print("推送完成！")
    else:
        print("推送失败，请检查配置")

if __name__ == "__main__":
    main()
