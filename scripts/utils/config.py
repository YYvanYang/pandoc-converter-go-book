import os
import yaml
from typing import Any, Dict

class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value

    def get_pandoc_options(self) -> list:
        """获取 Pandoc 选项"""
        options = []
        
        options.extend(['--pdf-engine', self.get('pdf.engine', 'xelatex')])
        
        template = self.get('pdf.template')
        if template:
            options.extend(['--template', template])
        
        if self.get('toc.enabled', True):
            options.append('--toc')
            options.extend(['--toc-depth', str(self.get('toc.depth', 3))])
        
        if self.get('processing.number-sections', True):
            options.append('--number-sections')
        
        extra_options = self.get('pdf.options', [])
        options.extend(extra_options)
        
        return options 