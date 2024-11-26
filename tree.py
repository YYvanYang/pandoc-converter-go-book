import os
import sys
from pathlib import Path

# 打印 Python 路径
print("Python Path:")
for path in sys.path:
    print(f"  - {path}")

# 打印当前目录
current_dir = os.getcwd()
print(f"\nCurrent Directory: {current_dir}")

# 递归打印目录结构
def print_tree(directory, prefix=""):
    """打印目录树结构"""
    path = Path(directory)
    print(f"{prefix}└── {path.name}/")
    prefix += "    "
    for item in sorted(path.iterdir()):
        if item.is_file():
            print(f"{prefix}└── {item.name}")
        elif item.is_dir() and not item.name.startswith('.'):
            print_tree(item, prefix)

print("\nProject Structure:")
print_tree(current_dir)