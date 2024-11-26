import yaml
from typing import Dict, Any

class Config:
    """配置加载器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                configs = list(yaml.safe_load_all(f))
                final_config = {}
                for config in configs:
                    if config:
                        final_config.update(config)
                return final_config
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 格式错误: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return key in self._config