.PHONY: all convert clean merge install install-deps

# 变量定义
PYTHON = python3
PIP = pip3
CONFIG = config/default.yaml
INPUT_DIR = data/input
OUTPUT_DIR = data/output
BOOK_DIR = $(INPUT_DIR)/book
MERGED_HTML = $(INPUT_DIR)/book/merged.html
DEFAULT_PDF = $(OUTPUT_DIR)/document.pdf
BREW = brew
TLMGR = tlmgr
XELATEX = xelatex
INKSCAPE = /opt/homebrew/bin/inkscape

# 获取当前日期 (格式: YYYYMMDD)
DATE := $(shell date +%Y%m%d)

# 设置输出文件名 (书名+日期)
OUTPUT_FILE = vue3-guide-$(DATE).pdf

# 默认目标：安装依赖，合并并转换
all: install merge
	$(MAKE) convert INPUT=$(MERGED_HTML) OUTPUT=$(DEFAULT_PDF)

# 检查并安装系统依赖
install-deps:
	@echo "检查并安装系统依赖..."
	@if ! command -v $(BREW) >/dev/null 2>&1; then \
		echo "错误: 请先安装 Homebrew"; \
		exit 1; \
	fi
	@if [ ! -f "$(INKSCAPE)" ]; then \
		echo "安装 Inkscape..."; \
		$(BREW) install inkscape; \
		if [ ! -f "$(INKSCAPE)" ]; then \
			echo "错误: Inkscape 安装失败，请手动检查安装路径"; \
			exit 1; \
		fi \
	else \
		echo "Inkscape 已安装"; \
		$(INKSCAPE) --version; \
	fi
	@if ! command -v $(TLMGR) >/dev/null 2>&1; then \
		echo "错误: 请先安装 TeX Live"; \
		exit 1; \
	fi
	@if ! command -v $(XELATEX) >/dev/null 2>&1; then \
		echo "错误: 未找到 xelatex 引擎，请确保完整安装了 TeX Live"; \
		exit 1; \
	fi
	@echo "检查 LaTeX 包..."
	@if ! $(TLMGR) info svg >/dev/null 2>&1; then \
		echo "安装 svg 包..."; \
		sudo $(TLMGR) update --self; \
		sudo $(TLMGR) install svg; \
	else \
		echo "svg 包已安装"; \
	fi
	@if ! kpsewhich xeCJK.sty >/dev/null 2>&1; then \
		echo "安装 xeCJK 包..."; \
		sudo $(TLMGR) install xecjk; \
	else \
		echo "xeCJK 包已安装"; \
	fi
	@if ! kpsewhich fontspec.sty >/dev/null 2>&1; then \
		echo "安装 fontspec 包..."; \
		sudo $(TLMGR) install fontspec; \
	else \
		echo "fontspec 包已安装"; \
	fi

# 安装依赖
install: install-deps
	@echo "安装 Python 依赖..."
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