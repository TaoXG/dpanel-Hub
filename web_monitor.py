import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def log_action(message):
    print(f"[{datetime.now().isoformat()}] {message}")

def read_current_date(file_type):
    try:
        with open(f'{file_type}.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        log_action(f"未找到 {file_type}.txt，将创建新文件")
        return ""

def download_file(url, save_path):
    try:
        log_action(f"开始下载: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        log_action(f"文件大小: {total_size} bytes")
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        log_action(f"文件保存成功: {save_path}")
        return True
    except Exception as e:
        log_action(f"下载失败: {str(e)}")
        return False

def scrape_channel():
    CHANNEL = os.getenv('CHANNEL_NAME', 'juejijianghu')
    BASE_URL = f"https://t.me/s/{CHANNEL}"
    
    try:
        log_action(f"开始抓取频道: {CHANNEL}")
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message', limit=20)
        
        for message in messages:
            # 解析逻辑保持不变...
            
            if data and download_file(data['url'], f'真心{file_type}.zip'):
                with open(f'{file_type}.txt', 'w') as f:
                    f.write(data['date_str'])
                log_action(f"成功更新 {file_type} 文件")
                
    except Exception as e:
        log_action(f"抓取过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    log_action("脚本启动")
    scrape_channel()
    log_action("脚本执行完成")
