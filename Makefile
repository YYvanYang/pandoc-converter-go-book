.PHONY: all convert clean

# 变量定义
PYTHON = python3
CONFIG = config/default.yaml
INPUT_DIR = data/input
OUTPUT_DIR = data/output

# 默认目标
all: convert

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
		"$(OUTPUT)"

# 清理输出
clean:
	rm -rf $(OUTPUT_DIR)/*
	mkdir -p $(OUTPUT_DIR) 