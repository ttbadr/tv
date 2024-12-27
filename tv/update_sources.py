import os
import requests

def has_content_changed(file_path, new_content):
    if not os.path.exists(file_path):
        return True
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        return old_content.strip() != new_content.strip()
    except Exception:
        return True

def get_file_extension(url):
    """根据URL确定文件扩展名"""
    if url.lower().endswith('.m3u8'):
        return '.m3u8'
    return '.m3u'

def fetch_url(url):
    """获取URL内容，支持重定向和自定义请求头"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/plain,application/x-mpegurl,application/vnd.apple.mpegurl,*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
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
    with open('tv/source.txt', 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            name, url = [x.strip() for x in line.split(',')]
            print(f"Fetching {name} from {url}")
            content = fetch_url(url)

            # 检查内容长度大于10KB
            if len(content) < 10 * 1024:
                print(f"Skipped {name} from {url} (content too short)")
                continue
            
            extension = get_file_extension(url)
            output_file = f'/www/tv/{name}{extension}'
            if has_content_changed(output_file, content):
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Successfully updated {name} from {url} (content changed)")
                has_updates = True
            else:
                print(f"Skipped {name} from {url} (content unchanged)")
        except requests.exceptions.RequestException as e:
            print(f"Network error while processing {url}: {str(e)}")
        except Exception as e:
            print(f"Error processing {line}: {str(e)}")
    
    # 创建标记文件来表示是否有更新
    with open('.has_updates', 'w') as f:
        f.write('yes' if has_updates else 'no')
    
    return has_updates

if __name__ == '__main__':
    os.makedirs('/www/tv', exist_ok=True)
    process_sources()