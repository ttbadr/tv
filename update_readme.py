import os

def get_file_list(directory):
    """获取目录下的所有文件信息"""
    files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith(('.json', '.m3u', '.m3u8')) and not file.startswith('.'):
                files.append({
                    'name': os.path.splitext(file)[0],
                    'file': file
                })
    return sorted(files, key=lambda x: x['name'].lower())

def update_readme(repo_owner, repo_name, proxy_prefix=None):
    """更新README.md文件
    
    Args:
        repo_owner: 仓库所有者
        repo_name: 仓库名称
        proxy_prefix: 代理前缀，如果为None则不使用代理
    """
    tvbox_files = get_file_list('tvbox')
    tv_files = get_file_list('tv')
    
    content = ['# TV Source List\n']
    
    if tvbox_files:
        content.append('\n## TVBox Sources\n')
        content.append('| Name | URL |\n')
        content.append('|------|-----|\n')
        for file in tvbox_files:
            raw_url = f'https://github.com/{repo_owner}/{repo_name}/raw/main/tvbox/{file["file"]}'
            final_url = f'{proxy_prefix}{raw_url}' if proxy_prefix else raw_url
            content.append(f'| {file["name"]} | {final_url} |\n')
    
    if tv_files:
        content.append('\n## TV Sources\n')
        content.append('| Name | URL |\n')
        content.append('|------|-----|\n')
        for file in tv_files:
            raw_url = f'https://github.com/{repo_owner}/{repo_name}/raw/main/tv/{file["file"]}'
            final_url = f'{proxy_prefix}{raw_url}' if proxy_prefix else raw_url
            content.append(f'| {file["name"]} | {final_url} |\n')
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    return bool(tvbox_files or tv_files)

if __name__ == '__main__':
    # 这里需要替换为实际的仓库所有者和仓库名
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'ttbadr')
    repo_name = os.getenv('GITHUB_REPOSITORY', 'tv').split('/')[-1]
    proxy_prefix = os.getenv('PROXY_PREFIX', 'https://www.ghproxy.cn/')
    update_readme(repo_owner, repo_name, proxy_prefix) 