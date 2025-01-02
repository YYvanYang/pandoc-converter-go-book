.PHONY: all convert clean merge install

# 变量定义
PYTHON = python3
PIP = pip3
CONFIG = config/default.yaml
INPUT_DIR = data/input
OUTPUT_DIR = data/output
BOOK_DIR = $(INPUT_DIR)/book
MERGED_HTML = $(INPUT_DIR)/book/merged.html
DEFAULT_PDF = $(OUTPUT_DIR)/document.pdf

# 获取当前日期 (格式: YYYYMMDD)
DATE := $(shell date +%Y%m%d)

# 设置输出文件名 (书名+日期)
OUTPUT_FILE = go语言圣经-$(DATE).pdf

# 默认目标：安装依赖，合并并转换
all: install merge
	$(MAKE) convert INPUT=$(MERGED_HTML) OUTPUT=$(DEFAULT_PDF)

# 安装依赖
install:
	@echo "安装依赖..."
	$(PIP) install -r requirements.txt
	@echo "复制 SF Mono 字体..."
	@if [ ! -f ~/Library/Fonts/SF-Mono-Regular.otf ]; then \
		mkdir -p ~/Library/Fonts && \
		cp /Applications/Xcode.app/Contents/SharedFrameworks/DVTUserInterfaceKit.framework/Versions/A/Resources/Fonts/SF-Mono-* ~/Library/Fonts/ || \
		echo "警告: SF Mono 字体复制失败，请确保已安装 Xcode"; \
	fi

# 合并HTML文件
merge:
	@echo "合并HTML文件..."
	$(PYTHON) scripts/merge.py \
		--input $(BOOK_DIR) \
		--output $(MERGED_HTML)

# 转换文档
convert:
	@if [ -z "$(INPUT)" ]; then \
		echo "Please specify input file with INPUT=<file>"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		echo "Please specify output file with OUTPUT=<file>"; \
		exit 1; \
	fi
	$(PYTHON) scripts/convert.py \
		--config $(CONFIG) \
		"$(INPUT)" \
		"data/output/$(OUTPUT_FILE)"

# 清理输出
clean:
	rm -rf $(OUTPUT_DIR)/*
	rm -f $(MERGED_HTML)
	mkdir -p $(OUTPUT_DIR) 