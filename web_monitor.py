import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# 配置参数
CHANNEL = os.getenv('CHANNEL_NAME', 'juejijianghu')
BASE_URL = f"https://t.me/s/{CHANNEL}"
FILE_PATTERNS = {
    '全量包': re.compile(r'真心(\d{8})-全量包\.zip'),
    '增量包': re.compile(r'真心(\d{8})-增量包\.zip')
}

def read_current_date(file_type):
    try:
        with open(f'{file_type}.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def parse_message(message_div):
    time_tag = message_div.find('time', class_='time')
    if not time_tag or not time_tag.has_attr('datetime'):
        return None
    
    date_str = time_tag['datetime'][:10]  # 获取YYYY-MM-DD
    document_div = message_div.find('div', class_='tgme_widget_message_document')
    if not document_div:
        return None
    
    file_name = document_div.find('div', class_='tgme_widget_message_document_name')。text
    file_url = document_div.find('a', class_='tgme_widget_message_document_link')['href']
    
    return {
        'file_name': file_name,
        'file_url': file_url,
        'date_str': date_str
    }

def scrape_channel():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message')
    
    newest_files = {key: None for key in FILE_PATTERNS.keys()}
    
    for message in messages:
        data = parse_message(message)
        if not data:
            continue
            
        for file_type, pattern in FILE_PATTERNS.items():
            match = pattern.search(data['file_name'])
            if match:
                date_str = match.group(1)
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if newest_files[file_type] is None or file_date > newest_files[file_type]['date']:
                    newest_files[file_type] = {
                        'url': data['file_url'],
                        'date': file_date,
                        'date_str': date_str
                    }

    for file_type, data in newest_files.items():
        if data is None:
            continue
            
        current_date = read_current_date(file_type)
        if current_date != data['date_str']:
            print(f"发现新{file_type}文件，日期: {data['date_str']}")
            download_file(data['url']， f'真心{file_type}.zip')
            
            with open(f'{file_type}.txt', 'w') as f:
                f.write(data['date_str'])
        else:
            print(f"{file_type}文件已是最新")

if __name__ == "__main__":
    scrape_channel()
