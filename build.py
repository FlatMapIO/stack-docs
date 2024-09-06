import os
import shutil
import subprocess

repos = [
    {
        "src": "https://github.com/solidjs/solid-docs",
        "path": "langs/en/",
        "include": [
            "api",
            "guides"
        ],
        "dest": "solid-docs",
    },
    {
        "src": "https://github.com/solidjs-community/solid-primitives",
        "path": "packages/{subfolder}/README.md",
        "dest": "solid-primitives/{subfolder}.md",
    },
    {
        "name": "solid-motionone",
        "src": "https://github.com/solidjs-community/solid-motionone",
        "path": "README.md",
        "dest": "solid-motionone.md",
    },
]

def clone_or_pull(repo_url, repo_path):
    if not os.path.exists(repo_path):
        subprocess.run(['git', 'clone', "--depth", "1", repo_url, repo_path], check=True)
    else:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)

def sync_files(src_path, dest_path, include=None, subfolder=None):
    if subfolder:
        src_path = src_path.replace('{subfolder}', subfolder)
        dest_path = dest_path.replace('{subfolder}', subfolder)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    if os.path.isfile(src_path):
        shutil.copy2(src_path, dest_path)
    else:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

        if include:
            os.makedirs(dest_path, exist_ok=True)
            for item in include:
                item_src = os.path.join(src_path, item)
                item_dest = os.path.join(dest_path, item)
                if os.path.exists(item_src):
                    if os.path.isfile(item_src):
                        shutil.copy2(item_src, item_dest)
                    else:
                        shutil.copytree(item_src, item_dest)
        else:
            shutil.copytree(src_path, dest_path)

if os.path.exists('docs'):
    shutil.rmtree('docs')
os.makedirs('docs')

for repo in repos:
    repo_name = repo.get('name') or repo['src'].split('/')[-1]
    repo_path = f"source/{repo_name}"

    # 克隆或更新仓库
    try:
        clone_or_pull(repo['src'], repo_path)
    except subprocess.CalledProcessError:
        print(f"Failed to clone or pull repository: {repo['src']}")
        continue

    # 同步文件
    src_path = os.path.join(repo_path, repo['path'])
    dest_path = f"docs/{repo['dest']}"

    if '{subfolder}' in src_path:
        for subfolder in os.listdir(os.path.dirname(src_path.replace('{subfolder}', ''))):
            if os.path.isdir(os.path.join(repo_path, 'packages', subfolder)):
                sync_files(src_path, dest_path, repo.get('include'), subfolder)
    else:
        sync_files(src_path, dest_path, repo.get('include'))

print("同步完成")

# 新增代码
def generate_readme():
    md_files = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith(('.md', '.mdx')):
                relative_path = os.path.relpath(os.path.join(root, file), '.')
                md_files.append(relative_path)

    with open('README.md', 'w') as readme:
        readme.write("# 文档索引\n\n")
        for file in sorted(md_files):
            readme.write(f"- [{file}]({file})\n")

generate_readme()
print("README.md 生成完成")
