import os
import json
import requests

def is_valid(content):
    # 检查内容是否包含字符串 "wallpaper",并且内容长度大于10KB
    return "wallpaper" in content and len(content) >= 10 * 1024

def has_content_changed(file_path, new_content):
    if not os.path.exists(file_path):
        return True
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        return old_content.strip() != new_content.strip()
    except Exception:
        return True

def fetch_url(url):
    """获取URL内容，支持重定向和自定义请求头"""
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Host': 'toby.v.nxog.top',
        'Connection': 'keep-alive',
        'Referer': 'https://toby.v.nxog.top/m/?b=æ¬§æ­'
    }
    
    session = requests.Session()
    # 允许重定向
    response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
    
    # 如果是GitHub的blob URL，转换为raw URL
    if 'github.com' in url and '/blob/' in response.url:
        raw_url = response.url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        response = session.get(raw_url, headers=headers, timeout=30)
    
    response.raise_for_status()  # 如果状态码不是200，抛出异常
    return response.text

def process_sources():
    has_updates = False
    with open('tvbox/source.txt', 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            name, url = [x.strip() for x in line.split(',')]
            print(f"Fetching {name} from {url}")
            content = fetch_url(url)
            
            if is_valid(content):
                output_file = f'/www/tvbox/{name}.json'
                if has_content_changed(output_file, content):
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Successfully updated {name} from {url} (content changed)")
                    has_updates = True
                else:
                    print(f"Skipped {name} from {url} (content unchanged)")
            else:
                print(f"Invalid JSON received from {url}")
        except requests.exceptions.RequestException as e:
            print(f"Network error while processing {url}: {str(e)}")
        except Exception as e:
            print(f"Error processing {line}: {str(e)}")
    
    # 创建标记文件来表示是否有更新
    with open('.has_updates', 'w') as f:
        f.write('yes' if has_updates else 'no')
    
    return has_updates

if __name__ == '__main__':
    os.makedirs('/www/tvbox', exist_ok=True)
    process_sources()