import os
import shutil
import subprocess
import re

# Hexo 项目根目录
HEXO_DIR = "/Users/yilingqinghan/Documents/BaiduPan/个人/简历网站/academic/hexo"  # 修改为您的 Hexo 项目路径

# 修正后的 public 文件夹目标目录
TARGET_DIR = "/Users/yilingqinghan/Documents/BaiduPan/个人/简历网站/academic"  # 修改为您想移动 public 文件夹的目标路径

# 正则表达式匹配绝对路径
ABSOLUTE_PATH_PATTERNS = [
    (re.compile(r'href="(/[^"]*)"', re.IGNORECASE), 'href="{}"'),
    (re.compile(r'src="(/[^"]*)"', re.IGNORECASE), 'src="{}"'),
    (re.compile(r'url\((["\'])?/([^\'")]+)\1\)', re.IGNORECASE), 'url({}{}{})')
]

# 正则表达式匹配外部资源路径（以 http:// 或 https:// 开头）
EXTERNAL_PATH_PATTERN = re.compile(r'(https?://)')


def run_command(command, cwd=None):
    """运行命令行命令"""
    try:
        subprocess.run(command, cwd=cwd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed with exit code {e.returncode}")
        exit(1)


def hexo_deploy():
    """运行 Hexo 的 clean、generate 和 deploy 命令"""
    print("Cleaning Hexo project...")
    run_command("hexo clean", cwd=HEXO_DIR)

    print("Generating Hexo static files...")
    run_command("hexo generate", cwd=HEXO_DIR)

    print("Deploying Hexo project (optional)...")
    run_command("hexo deploy", cwd=HEXO_DIR)  # 如果不需要 Hexo 的 deploy，可以注释掉这一行


def calculate_relative_path(file_path, target_path):
    """计算相对路径"""
    # 获取文件的目录深度
    file_dir = os.path.dirname(file_path)
    depth = len(file_dir.split(os.sep)) - len(os.path.join(HEXO_DIR, "public").split(os.sep))

    # 如果路径以 `/` 开头（绝对路径），移除前导斜杠
    if target_path.startswith("/"):
        target_path = target_path[1:]

    # 根据深度计算 "../" 的数量
    relative_prefix = '../' * depth
    return os.path.join(relative_prefix, target_path).replace("\\", "/")  # 确保路径格式兼容


def fix_paths_in_file(file_path):
    """修改文件中的绝对路径为相对路径"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    original_content = content

    # 使用正则表达式替换绝对路径为动态相对路径
    for pattern, replacement in ABSOLUTE_PATH_PATTERNS:
        def replacer(match):
            # 获取匹配到的路径
            target_path = match.group(1) if len(match.groups()) == 1 else match.group(2)

            # 排除外部资源
            if EXTERNAL_PATH_PATTERN.match(target_path):
                return match.group(0)  # 保持原样，不修改

            # 动态计算相对路径
            relative_path = calculate_relative_path(file_path, target_path)
            if "{}" in replacement:
                return replacement.format(relative_path)
            else:
                return replacement.replace(match.group(0), relative_path)

        content = pattern.sub(replacer, content)

    # 如果内容被修改，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated paths in: {file_path}")


def process_directory(directory):
    """递归处理目录中的所有文件"""
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            # 只处理 HTML 和 CSS 文件
            if full_path.endswith(('.html', '.css')):
                fix_paths_in_file(full_path)


def fix_paths():
    """修正路径"""
    print("Fixing paths in Hexo public directory...")
    process_directory(os.path.join(HEXO_DIR, "public"))


def move_public_folder():
    """将 public 文件夹整体移动到目标目录"""
    source_dir = os.path.join(HEXO_DIR, "public")

    # 确保目标目录存在，如果不存在则创建
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    # 移动 public 文件夹到目标目录
    print(f"Moving public folder to: {TARGET_DIR}...")
    target_public_dir = os.path.join(TARGET_DIR, "public")
    if os.path.exists(target_public_dir):
        shutil.rmtree(target_public_dir)  # 删除已有的 public 文件夹
    shutil.move(source_dir, target_public_dir)


if __name__ == "__main__":
    print("Starting Hexo deployment workflow...")

    # 1. Hexo 部署
    hexo_deploy()

    # 2. 修正路径
    fix_paths()

    # 3. 移动 public 文件夹
    move_public_folder()

    print("Hexo deployment workflow completed!")