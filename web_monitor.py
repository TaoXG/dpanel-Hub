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
    response.raise_for_status()  # 检查请求是否成功
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def parse_message(message_div):
    try:
        # 更健壮的时间解析
        time_tag = message_div.find('time', class_='time')
        if not time_tag or not time_tag.has_attr('datetime'):
            return None
        
        # 更安全的文档查找
        document_wrap = message_div.find('div', class_='tgme_widget_message_document_wrap')
        if not document_wrap:
            return None
            
        document_info = document_wrap.find('div', class_='tgme_widget_message_document')
        if not document_info:
            return None
            
        file_name_elem = document_info.find('div', class_='tgme_widget_message_document_name')
        file_url_elem = document_info.find('a', class_='tgme_widget_message_document_link')
        
        if not file_name_elem or not file_url_elem:
            return None
            
        return {
            'file_name': file_name_elem.text.strip(),
            'file_url': file_url_elem['href'],
            'date_str': time_tag['datetime'][:10]
        }
    except Exception as e:
        print(f"解析消息时出错: {str(e)}")
        return None

def scrape_channel():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(BASE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message', limit=20)
        
        newest_files = {key: None for key in FILE_PATTERNS.keys()}
        
        for message in messages:
            data = parse_message(message)
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
                                'url': data['file_url'],
                                'date': file_date,
                                'date_str': date_str
                            }
                    except ValueError:
                        continue

        for file_type, data in newest_files.items():
            if data is None:
                print(f"未找到新的{file_type}文件")
                continue
                
            current_date = read_current_date(file_type)
            if current_date != data['date_str']:
                print(f"发现新{file_type}文件，日期: {data['date_str']}")
                try:
                    download_file(data['url'], f'真心{file_type}.zip')
                    with open(f'{file_type}.txt', 'w') as f:
                        f.write(data['date_str'])
                except Exception as e:
                    print(f"下载文件失败: {str(e)}")
            else:
                print(f"{file_type}文件已是最新")

    except Exception as e:
        print(f"抓取频道时发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    scrape_channel()
