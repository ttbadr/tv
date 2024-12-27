import os
import json
import requests
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from update_readme import update_readme

def is_valid_json(content):
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

def has_content_changed(file_path, new_content):
    if not os.path.exists(file_path):
        return True
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        # 比较JSON内容（忽略空格和格式差异）
        old_json = json.loads(old_content)
        new_json = json.loads(new_content)
        return json.dumps(old_json, sort_keys=True) != json.dumps(new_json, sort_keys=True)
    except Exception:
        return True

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
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                if is_valid_json(content):
                    output_file = f'tvbox/{name}.json'
                    if has_content_changed(output_file, content):
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Successfully updated {name} from {url} (content changed)")
                        has_updates = True
                    else:
                        print(f"Skipped {name} from {url} (content unchanged)")
                else:
                    print(f"Invalid JSON received from {url}")
            else:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error processing {line}: {str(e)}")
    
    # 创建标记文件来表示是否有更新
    with open('.has_updates', 'w') as f:
        f.write('yes' if has_updates else 'no')
    
    return has_updates

if __name__ == '__main__':
    os.makedirs('tvbox', exist_ok=True)
    has_updates = process_sources()
    # 如果有更新，就更新 README
    if has_updates:
        try:
            # 从环境变量获取仓库信息和代理前缀
            repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'owner')
            repo_name = os.getenv('GITHUB_REPOSITORY', 'repo').split('/')[-1]
            proxy_prefix = os.getenv('PROXY_PREFIX', 'https://www.ghproxy.cn/')
            update_readme(repo_owner, repo_name, proxy_prefix)
            print("Successfully updated README.md")
        except Exception as e:
            print(f"Failed to update README.md: {str(e)}") 