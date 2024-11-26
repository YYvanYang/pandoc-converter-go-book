import os
import sys
import argparse
from pathlib import Path

def should_ignore(path, root_dir, ignore_patterns):
    """检查是否应该忽略该路径"""
    try:
        # 计算相对于根目录的路径
        rel_path = str(path.relative_to(root_dir))
        
        # 处理隐藏文件
        if path.name.startswith('.'):
            return True
            
        for pattern in ignore_patterns:
            pattern = pattern.rstrip('/')  # 移除末尾的斜杠
            
            # 处理精确匹配
            if rel_path == pattern:
                return True
                
            # 处理目录通配符
            if pattern.endswith('/'):
                if path.is_dir() and rel_path.startswith(pattern):
                    return True
                    
            # 处理通配符模式
            try:
                if path.match(pattern):
                    return True
            except Exception:
                continue
                
        return False
    except ValueError:  # 处理路径计算异常
        return False

def read_gitignore(root_dir):
    """读取 .gitignore 文件"""
    gitignore_path = Path(root_dir) / '.gitignore'
    ignore_patterns = []
    
    # 添加默认忽略模式
    ignore_patterns.extend([
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git/',
        '.idea/',
        '.vscode/',
        '*.swp',
        '.DS_Store'
    ])
    
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
        except Exception as e:
            print(f"警告: 读取 .gitignore 文件时出错: {str(e)}")
    
    return ignore_patterns

def print_tree(directory, prefix="", ignore_patterns=None, root_dir=None):
    """打印目录树结构"""
    path = Path(directory)
    if root_dir is None:
        root_dir = path
    if ignore_patterns is None:
        ignore_patterns = []
    
    if should_ignore(path, root_dir, ignore_patterns):
        return
        
    # 显示根目录时不显示完整路径，只显示目录名
    if path == root_dir:
        print(f"{prefix}└── {path.name}/")
    else:
        print(f"{prefix}└── {path.name}")
    prefix += "    "
    
    try:
        # 过滤掉隐藏文件和被忽略的文件
        items = sorted(path.iterdir())
        for item in items:
            if should_ignore(item, root_dir, ignore_patterns):
                continue
            if item.is_file():
                print(f"{prefix}└── {item.name}")
            elif item.is_dir():
                print_tree(item, prefix, ignore_patterns, root_dir)
    except PermissionError:
        print(f"{prefix}└── (访问被拒绝)")
    except Exception as e:
        print(f"{prefix}└── (错误: {str(e)})")

def main():
    parser = argparse.ArgumentParser(
        description='目录树生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python tree.py                 # 显示当前目录的树结构
  python tree.py /path/to/dir    # 显示指定目录的树结构
  python tree.py -h              # 显示此帮助信息

说明:
  - 自动读取并应用目标目录中的 .gitignore 规则
  - 忽略以 . 开头的隐藏文件和目录
  - 按字母顺序排序显示文件和目录
        '''
    )
    parser.add_argument('directory', 
                       nargs='?', 
                       default=os.getcwd(),
                       help='要显示的目录路径（默认为当前目录）')
    args = parser.parse_args()

    try:
        directory = Path(args.directory).resolve()
        if not directory.exists():
            print(f"错误: 目录 '{directory}' 不存在")
            sys.exit(1)
        if not directory.is_dir():
            print(f"错误: '{directory}' 不是一个目录")
            sys.exit(1)
            
        ignore_patterns = read_gitignore(directory)
        print(f"\n目录结构: {directory}")
        print_tree(directory, ignore_patterns=ignore_patterns, root_dir=directory)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()