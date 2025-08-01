import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration management for the transaction analyzer."""
    
    DEFAULT_CONFIG = {
        'etherscan': {
            'api_key': '', # This is set in the environment variables
            'base_url': 'https://api.etherscan.io/api',
        },
        'logging': {
            'level': 'INFO',
            'format': '%(levelname)s - %(message)s',
            'file': 'transaction_analyzer.log'
        }
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_environment_variables()
        self.validate_config()
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        load_dotenv()
        self.config['etherscan']['api_key'] = os.getenv('ETHERSCAN_API_KEY', '')

    def validate_config(self):
        """Validate the configuration."""
        
        # Raise an error if the API key is not set in the environment variables
        if not self.config['etherscan']['api_key']:
            raise ValueError("ETHERSCAN_API_KEY is not set in the environment variables")
    
    def setup_logging(self):
        """Set up logging based on configuration."""
        log_level = getattr(logging, self.config['logging']['level'].upper())
        log_format = self.config['logging']['format']
        log_file = self.config['logging']['file']
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")


def get_config() -> Config:
    """Get a configured Config instance."""
    return Config() 