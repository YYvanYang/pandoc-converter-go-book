import os
import re
import shutil
from pathlib import Path
import argparse
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
import hashlib
from utils.config import Config

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除特殊字符"""
    # 获取文件扩展名
    name, ext = os.path.splitext(filename)
    # 使用 MD5 哈希创建安全的文件名
    safe_name = hashlib.md5(name.encode()).hexdigest()[:8]
    return f"{safe_name}{ext}"

def copy_and_rename_image(src_path: Path, images_dir: Path) -> Path:
    """复制并重命名图片文件"""
    if not src_path.exists():
        return None
    
    # 创建图片目录
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成安全的文件名
    safe_filename = sanitize_filename(src_path.name)
    dest_path = images_dir / safe_filename
    
    # 复制文件
    try:
        shutil.copy2(src_path, dest_path)
        return dest_path
    except Exception as e:
        print(f"警告: 复制图片失败 {src_path}: {str(e)}")
        return None

def fix_image_path(img_src: str, input_path: Path, images_dir: Path) -> str:
    """修复图片路径"""
    try:
        # 如果是完整的 URL，尝试获取本地文件
        if urlparse(img_src).scheme:
            img_filename = Path(urlparse(img_src).path).name
            # 先检查直接路径
            local_img = input_path / img_filename
            if not local_img.exists():
                # 再检查 images 目录
                local_img = input_path / 'images' / img_filename
        else:
            # 处理相对路径
            img_path = Path(img_src)
            if img_src.startswith('./'):
                img_path = Path(img_src[2:])
            elif img_src.startswith('../'):
                img_path = Path(img_src[3:])
            
            local_img = input_path / img_path
        
        # 如果找到图片，复制到新位置
        if local_img.exists():
            new_path = copy_and_rename_image(local_img, images_dir)
            if new_path:
                return str(new_path)
        
        return None
    except Exception as e:
        print(f"警告: 处理图片路径时出错 {img_src}: {str(e)}")
        return None

def merge_html_files(input_dir: str, output_file: str):
    input_path = Path(input_dir)
    output_path = Path(output_file)
    
    # 使用 Config 类加载配置
    config = Config("config/default.yaml")
    
    # 从配置获取元数据
    metadata = config.get("metadata", {})
    authors = metadata.get("authors", [])
    author_prefix = metadata.get("author_prefix", "译者:")
    author_text = f"{author_prefix} {', '.join(authors)}"
    
    # 定义 CSS 样式
    css_styles = """
        body { max-width: 800px; margin: 0 auto; padding: 20px; }
        img { max-width: 100%; height: auto; }
        pre { white-space: pre-wrap; }
        code { background: #f5f5f5; padding: 2px 5px; }
    """
    
    # 创建新的文档结构
    html_template = f"""
    <!DOCTYPE html>
    <html lang="{metadata.get('language', 'zh-CN')}">
    <head>
        <meta charset="UTF-8">
        <meta name="author" content="{author_text}">
        <meta name="dc.creator" content="{author_text}">
        <meta name="dc.title" content="{metadata.get('title', '')}">
        <meta name="dc.language" content="{metadata.get('language', 'zh-CN')}">
        <meta name="dc.rights" content="{metadata.get('rights', '')}">
        <title>{metadata.get('title', '')}</title>
        <style>
            {css_styles}
        </style>
    </head>
    <body>
        <div class="content"></div>
    </body>
    </html>
    """
    
    template_soup = BeautifulSoup(html_template, "html.parser")
    
    # 创建图片目录
    images_dir = output_path.parent / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取主文件
    with open(input_path / "index.html", "r", encoding="utf-8") as f:
        main_soup = BeautifulSoup(f.read(), "html.parser")
    
    # 获取导航栏中的章节链接
    nav = main_soup.find("nav", class_="sidebar")
    if not nav:
        raise ValueError("无法找到导航栏")
    
    # 收集所有章节链接
    chapters = []
    for link in nav.find_all("a"):
        href = link.get("href")
        if href:
            href = unquote(href.replace("./", ""))
            chapters.append(href)
    
    # 创建新的内容容器
    merged_content = []
    
    # 合并所有文件
    for chapter in chapters:
        chapter_path = input_path / chapter
        if chapter_path.exists():
            print(f"处理章节: {chapter}")
            with open(chapter_path, "r", encoding="utf-8") as f:
                chapter_soup = BeautifulSoup(f.read(), "html.parser")
                
                # 获取主要内容
                content = chapter_soup.find("div", id="content")
                if not content:
                    content = chapter_soup.find("main")
                if not content:
                    content = chapter_soup.find("div", class_="content")
                
                if content:
                    # 移除导航栏和不需要的元素
                    for nav in content.find_all("nav"):
                        nav.decompose()
                    for sidebar in content.find_all("div", class_="sidebar"):
                        sidebar.decompose()
                    
                    # 处理图片
                    for img in content.find_all("img"):
                        src = img.get("src")
                        if src:
                            new_src = fix_image_path(src, input_path, images_dir)
                            if new_src:
                                img["src"] = new_src
                            else:
                                # 如果找不到图片，移除图片标签
                                print(f"警告: 找不到图片 {src}，移除此图片")
                                img.decompose()
                    
                    merged_content.append(str(content))
                else:
                    print(f"警告: 在 {chapter} 中未找到内容")
        else:
            print(f"警告: 文件不存在 {chapter}")
    
    # 将合并的内容插入到模板中
    content_div = template_soup.find("div", class_="content")
    content_div.append(BeautifulSoup("\n".join(merged_content), "html.parser"))
    
    # 保存合并后的文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(template_soup))
    
    print(f"合并完成: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="合并HTML文件")
    parser.add_argument("--input", required=True, help="输入目录")
    parser.add_argument("--output", required=True, help="输出文件")
    args = parser.parse_args()
    
    merge_html_files(args.input, args.output)

if __name__ == "__main__":
    main() 