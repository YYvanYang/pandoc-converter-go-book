#!/usr/bin/env python3

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Optional

# 获取 scripts 目录的路径
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# 直接从当前目录导入
from utils.pandoc import PandocConverter
from utils.config import Config

class DocumentConverter:
    """文档转换器"""
    
    def __init__(self, config_path: str = "config/default.yaml"):
        self.logger = self._setup_logging()
        self.config = Config(config_path)
        self.converter = PandocConverter(self.config)

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def convert(self, input_path: str, output_path: str) -> bool:
        """执行文档转换"""
        try:
            self.logger.info(f"Starting conversion: {input_path} -> {output_path}")
            
            input_path = Path(input_path)
            if not input_path.exists():
                self.logger.error(f"Input file not found: {input_path}")
                return False
                
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            success = self.converter.convert(str(input_path), str(output_path))
            
            if success:
                self.logger.info("Conversion completed successfully")
                return True
            else:
                self.logger.error("Conversion failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Conversion error: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML documents to PDF using Pandoc"
    )
    parser.add_argument("input", help="Input HTML file path")
    parser.add_argument("output", help="Output PDF file path")
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    converter = DocumentConverter(args.config)
    success = converter.convert(args.input, args.output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 