import subprocess
import logging
from pathlib import Path
from datetime import datetime

class PandocConverter:
    """使用 Pandoc 进行文档转换"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def convert(self, input_path: str, output_path: str) -> bool:
        """转换 HTML 到 PDF"""
        try:
            # 获取项目根目录
            project_root = Path(__file__).resolve().parent.parent.parent
            input_dir = Path(input_path).parent
            
            # 构建模板相关路径
            template_dir = project_root / 'templates' / 'latex'
            template_path = template_dir / 'main.tex'
            
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 从配置获取元数据
            authors = self.config.get("metadata", {}).get("authors", [])
            author_prefix = self.config.get("metadata", {}).get("author_prefix", "译者:")
            author_text = f"{author_prefix} {', '.join(authors)}"
            metadata = self.config.get("metadata", {})
            
            # Pandoc 命令
            cmd = [
                'pandoc',
                '--pdf-engine=xelatex',
                '-f', 'html',
                '-t', 'pdf',
                '--template', str(template_path),
                '--extract-media', str(output_dir),
                '--wrap=none',
                '-V', 'documentclass=article',
                '-V', 'CJKmainfont=PingFang SC',
                '-V', 'geometry=margin=2.5cm',
                '-V', f'title={metadata.get("title", "")}',
                '-V', f'author={author_text}',
                '--pdf-engine-opt=-shell-escape',
                '--metadata', f'title={metadata.get("title", "")}',
                '--metadata', f'author={author_text}',
                '--metadata', f'creator={metadata.get("creator", "")}',
                '--metadata', f'producer={metadata.get("producer", "")}',
                '--metadata', f'keywords={metadata.get("keywords", "")}',
                '--metadata', f'subject={metadata.get("subject", "")}',
                '-o', output_path,
                input_path
            ]
            
            self.logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info("文档转换成功")
                return True
            else:
                self.logger.error(f"Pandoc 转换失败:\n{result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"转换过程出错: {str(e)}")
            return False