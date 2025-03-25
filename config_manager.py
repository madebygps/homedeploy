import json
import os

from pathlib import Path

class ConfigManager:
    def __init__(self, base_dir):
        self.config_dir = Path(base_dir).parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        self.global_config_path = self.config_dir / "global.json"
        self._init_global_config()
    
    def _init_global_config(self):
        """Create global init if it does not exist"""
        if not self.global_config_path.exists():
            default_config = {
                "local": {
                    "ssh_username": os.getlogin()},
                "environments":["dev","stage", "prod"]
            }
            
            with open(self.global_config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
    def get_app_config(self, app_name, env_name="dev"):
        """Get config for an app and environment"""
        config_file = self.config_dir / f"{app_name}.json"
        if not config_file.exists():
            return None
        
        with open(config_file, 'r') as f:
            app_config = json.load(f)
            
        return app_config.get(env_name, {})
    
    def create_app_config(self, app_name):
        """Create a new application configuration"""
        config_file = self.config_dir / f"{app_name}.json"
        default_config = {
            "dev": {
                "needs_venv": True,
                "startup_script": "start.sh",
                "port": 8000
            },
            "stage": {
                "needs_venv": True,
                "startup_script": "start.sh",
                "port": 8001
            },
            "prod": {
                "needs_venv": True,
                "startup_script": "start.sh",
                "port": 80
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    def get_global_config(self):
        """Get global configuration settings"""
        with open(self.global_config_path, 'r') as f:
            return json.load(f)
        
    def save_global_config(self, config_data):
        """Save global configuration"""
        with open(self.global_config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
        