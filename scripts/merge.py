import os
import re
import shutil
from pathlib import Path
import argparse
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
import hashlib
from utils.config import Config

def extract_sidebar_structure(soup):
    """从HTML文档中提取侧边栏结构"""
    sidebar = soup.find("aside", class_="VPSidebar")
    if not sidebar:
        return []
    
    structure = []
    groups = sidebar.find_all("div", class_="group")
    
    for group in groups:
        section = group.find("section", class_="VPSidebarGroup")
        if not section:
            continue
            
        title = section.find("h2", class_="title-text")
        if not title:
            continue
            
        group_data = {
            "title": title.get_text(strip=True),
            "items": []
        }
        
        links = section.find_all("a", class_="link")
        for link in links:
            href = link.get("href", "")
            if href.startswith("/"):
                href = href[1:]  # 移除开头的斜杠
            
            text = link.find("p", class_="link-text")
            if text:
                group_data["items"].append({
                    "title": text.get_text(strip=True),
                    "href": href
                })
        
        if group_data["items"]:
            structure.append(group_data)
    
    return structure

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
        header.file-name { 
            font-weight: bold;
            color: #333;
            padding: 5px 10px;
            margin-bottom: 5px;
            background-color: #f8f8f8;
            border-bottom: 1px solid #ddd;
            text-decoration: underline;
            text-decoration-style: solid;
            font-family: monospace;
        }
        .toc { margin-bottom: 20px; }
        .toc h2 { margin-bottom: 10px; }
        .toc-group { margin-bottom: 15px; }
        .toc-group-title { 
            font-weight: bold;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        .toc-items { 
            margin-left: 20px;
            list-style-type: none;
            padding-left: 0;
        }
        .toc-item { margin-bottom: 3px; }
        .toc-item a {
            color: #476582;
            text-decoration: none;
        }
        .toc-item a:hover {
            color: #3eaf7c;
            text-decoration: underline;
        }
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
        <div class="toc"></div>
        <div class="content"></div>
    </body>
    </html>
    """
    
    template_soup = BeautifulSoup(html_template, "html.parser")
    
    # 创建图片目录
    images_dir = output_path.parent / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取主文件
    with open(input_path / "guide/introduction.html", "r", encoding="utf-8") as f:
        main_soup = BeautifulSoup(f.read(), "html.parser")
    
    # 提取侧边栏结构
    structure = extract_sidebar_structure(main_soup)
    
    # 创建目录
    toc_div = template_soup.find("div", class_="toc")
    toc_div.append(template_soup.new_tag("h2", string="目录"))
    
    for group in structure:
        group_div = template_soup.new_tag("div", attrs={"class": "toc-group"})
        group_title = template_soup.new_tag("div", attrs={"class": "toc-group-title"})
        group_title.string = group["title"]
        group_div.append(group_title)
        
        items_ul = template_soup.new_tag("ul", attrs={"class": "toc-items"})
        for item in group["items"]:
            item_li = template_soup.new_tag("li", attrs={"class": "toc-item"})
            item_a = template_soup.new_tag("a", href=f"#{item['href']}")
            item_a.string = item["title"]
            item_li.append(item_a)
            items_ul.append(item_li)
        
        group_div.append(items_ul)
        toc_div.append(group_div)
    
    # 合并所有文件
    merged_content = []
    for group in structure:
        for item in group["items"]:
            file_path = input_path / item["href"]
            if file_path.exists():
                print(f"处理章节: {item['href']}")
                with open(file_path, "r", encoding="utf-8") as f:
                    chapter_soup = BeautifulSoup(f.read(), "html.parser")
                    
                    # 获取主要内容
                    content = chapter_soup.find("div", class_="vt-doc")
                    if content:
                        # 处理图片
                        for img in content.find_all("img"):
                            src = img.get("src")
                            if src:
                                new_src = fix_image_path(src, input_path, images_dir)
                                if new_src:
                                    img["src"] = new_src
                                else:
                                    print(f"警告: 找不到图片 {src}，移除此图片")
                                    img.decompose()
                        
                        # 添加章节锚点
                        section = template_soup.new_tag("section", id=item["href"])
                        section.append(content)
                        merged_content.append(str(section))
                    else:
                        print(f"警告: 在 {item['href']} 中未找到内容")
            else:
                print(f"警告: 文件不存在 {item['href']}")
    
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