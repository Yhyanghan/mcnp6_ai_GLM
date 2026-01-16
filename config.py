import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MCNP6_PATH = os.getenv('MCNP6_PATH', 'mcnp6.exe')
    MCNP6_CMD = os.getenv('MCNP6_CMD', 'mcnp6')
    MCNP6_ENV_BAT = os.getenv('MCNP6_ENV_BAT', '')
    MCNP6_WORKSPACE = os.getenv('MCNP6_WORKSPACE', './workspace')
    
    AI_MODE = os.getenv('AI_MODE', 'online')
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_API_BASE = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '2000'))
    
    AI_LOCAL_ENDPOINT = os.getenv('AI_LOCAL_ENDPOINT', 'http://localhost:11434/api/generate')
    AI_LOCAL_MODEL = os.getenv('AI_LOCAL_MODEL', 'llama2')
    
    DEFAULT_ENCODING = os.getenv('DEFAULT_ENCODING', 'utf-8')
    AUTO_SAVE_INTERVAL = int(os.getenv('AUTO_SAVE_INTERVAL', '300'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
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
