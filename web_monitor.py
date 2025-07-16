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

def parse_message(message):
    try:
        time_elem = message.find('time', {'datetime': True})
        if not time_elem:
            return None

        file_elem = message.find('a', {'href': re.compile(r'//cdn\.telesco\.pe/')})
        if not file_elem:
            return None

        file_name = file_elem.text.strip()
        file_url = file_elem['href']
        
        if not file_url.startswith('http'):
            file_url = 'https:' + file_url

        return {
            'file_name': file_name,
            'file_url': file_url,
            'date_str': time_elem['datetime'][:10]
        }
    except Exception as e:
        log_action(f"解析消息出错: {str(e)}")
        return None

def scrape_channel():
    CHANNEL = os.getenv('CHANNEL_NAME', 'juejijianghu')
    BASE_URL = f"https://t.me/s/{CHANNEL}"
    FILE_PATTERNS = {
        '全量包': re.compile(r'真心(\d{8})-全量包\.zip'),
        '增量包': re.compile(r'真心(\d{8})-增量包\.zip')
    }
    
    try:
        log_action(f"开始抓取频道: {CHANNEL}")
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message', limit=20)
        
        newest_files = {key: None for key in FILE_PATTERNS.keys()}
        
        for message in messages:
            data = parse_message(message)  # 在此处定义data变量
            if not data:
                continue
                
            for file_type, pattern in FILE_PATTERNS.items():
                match = pattern.search(data['file_name'])
                if match:
                    date_str = match.group(1)
                    try:
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if newest_files[file_type] is None or file_date > newest_files[file_type]['date']:
                            newest_files[file_type] = {
                                'url': data['url'],
                                'date': file_date,
                                'date_str': date_str
                            }
                    except ValueError:
                        continue

        for file_type, data in newest_files.items():  # 这里的data是newest_files的值
            if data is None:
                log_action(f"未找到新的{file_type}文件")
                continue
                
            current_date = read_current_date(file_type)
            if current_date != data['date_str']:
                log_action(f"发现新{file_type}文件，日期: {data['date_str']}")
                if download_file(data['url'], f'真心{file_type}.zip'):
                    with open(f'{file_type}.txt', 'w') as f:
                        f.write(data['date_str'])
            else:
                log_action(f"{file_type}文件已是最新")

    except Exception as e:
        log_action(f"抓取过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    log_action("脚本启动")
    scrape_channel()
    log_action("脚本执行完成")
