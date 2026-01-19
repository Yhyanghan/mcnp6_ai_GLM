import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

env_file = application_path / '.env'
load_dotenv(env_file)

class Config:
    # 默认配置值
    _DEFAULTS = {
        'MCNP6_PATH': 'mcnp6.exe',
        'MCNP6_CMD': 'mcnp6',
        'MCNP6_ENV_BAT': '',
        'MCNP6_WORKSPACE': './workspace',
        'AI_MODE': 'online',
        'AI_API_KEY': '',
        'AI_API_BASE': 'https://api.openai.com/v1',
        'AI_MODEL': 'gpt-4',
        'AI_TEMPERATURE': '0.7',
        'AI_MAX_TOKENS': '2000',
        'AI_LOCAL_ENDPOINT': 'http://localhost:11434/api/generate',
        'AI_LOCAL_MODEL': 'llama2',
        'DEFAULT_ENCODING': 'utf-8',
        'AUTO_SAVE_INTERVAL': '300',
        'LOG_LEVEL': 'INFO',
        'RECENT_FILES': '',
    }
    
    @classmethod
    def _load_config(cls):
        """从环境变量加载所有配置"""
        cls.MCNP6_PATH = os.getenv('MCNP6_PATH', cls._DEFAULTS['MCNP6_PATH'])
        cls.MCNP6_CMD = os.getenv('MCNP6_CMD', cls._DEFAULTS['MCNP6_CMD'])
        cls.MCNP6_ENV_BAT = os.getenv('MCNP6_ENV_BAT', cls._DEFAULTS['MCNP6_ENV_BAT'])
        cls.MCNP6_WORKSPACE = os.getenv('MCNP6_WORKSPACE', cls._DEFAULTS['MCNP6_WORKSPACE'])
        
        cls.AI_MODE = os.getenv('AI_MODE', cls._DEFAULTS['AI_MODE'])
        cls.AI_API_KEY = os.getenv('AI_API_KEY', cls._DEFAULTS['AI_API_KEY'])
        cls.AI_API_BASE = os.getenv('AI_API_BASE', cls._DEFAULTS['AI_API_BASE'])
        cls.AI_MODEL = os.getenv('AI_MODEL', cls._DEFAULTS['AI_MODEL'])
        cls.AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', cls._DEFAULTS['AI_TEMPERATURE']))
        cls.AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', cls._DEFAULTS['AI_MAX_TOKENS']))
        
        cls.AI_LOCAL_ENDPOINT = os.getenv('AI_LOCAL_ENDPOINT', cls._DEFAULTS['AI_LOCAL_ENDPOINT'])
        cls.AI_LOCAL_MODEL = os.getenv('AI_LOCAL_MODEL', cls._DEFAULTS['AI_LOCAL_MODEL'])
        
        cls.DEFAULT_ENCODING = os.getenv('DEFAULT_ENCODING', cls._DEFAULTS['DEFAULT_ENCODING'])
        cls.AUTO_SAVE_INTERVAL = int(os.getenv('AUTO_SAVE_INTERVAL', cls._DEFAULTS['AUTO_SAVE_INTERVAL']))
        cls.LOG_LEVEL = os.getenv('LOG_LEVEL', cls._DEFAULTS['LOG_LEVEL'])
        cls.RECENT_FILES = os.getenv('RECENT_FILES', cls._DEFAULTS['RECENT_FILES'])
    
    @classmethod
    def reload(cls):
        """重新加载配置"""
        load_dotenv(env_file, override=True)
        cls._load_config()
    
    @classmethod
    def get_recent_files(cls):
        """获取最近文件列表"""
        if not cls.RECENT_FILES:
            return []
        return [f for f in cls.RECENT_FILES.split('|') if f and os.path.exists(f)]
    
    @classmethod
    def add_recent_file(cls, file_path):
        """添加最近文件"""
        recent = cls.get_recent_files()
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        recent = recent[:10]  # 最多保留10个
        cls.RECENT_FILES = '|'.join(recent)
        cls._save_recent_files()
    
    @classmethod
    def _save_recent_files(cls):
        """保存最近文件到.env"""
        try:
            env_path = str(env_file)
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                found = False
                new_lines = []
                for line in lines:
                    if line.strip().startswith('RECENT_FILES='):
                        new_lines.append(f'RECENT_FILES={cls.RECENT_FILES}\n')
                        found = True
                    else:
                        new_lines.append(line)
                
                if not found:
                    new_lines.append(f'RECENT_FILES={cls.RECENT_FILES}\n')
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
        except Exception as e:
            pass  # 静默处理保存失败
    
    @classmethod
    def validate(cls):
        """验证配置"""
        errors = []
        if cls.AI_MODE == 'online' and not cls.AI_API_KEY:
            errors.append('AI_API_KEY is not set (required for online mode)')
        if cls.AI_MODE == 'local' and not cls.AI_LOCAL_ENDPOINT:
            errors.append('AI_LOCAL_ENDPOINT is not set (required for local mode)')
        if not os.path.exists(cls.MCNP6_PATH):
            errors.append(f'MCNP6_PATH does not exist: {cls.MCNP6_PATH}')
        if cls.MCNP6_CMD and not os.path.exists(cls.MCNP6_CMD):
            errors.append(f'MCNP6_CMD does not exist: {cls.MCNP6_CMD}')
        return errors

# 初始化加载配置
Config._load_config()
