import shutil
import subprocess
import sys
from pathlib import Path           

class LocalDeployer:
    def __init__(self, config_manager, base_dir):
        self.config_manager = config_manager
        self.base_dir = Path(base_dir).parent
        self.deployments_dir = self.base_dir / "deployments"
        self.logs_dir = self.base_dir / "logs"
        self.deployments_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
    def deploy(self, app_name, app_path, env_name="dev"):
        """Deploy an app to local NAS"""
        print(f"Deploying {app_name} to {env_name}")
        
        config = self.config_manager.get_app_config(app_name, env_name)
        if not config:
            print(f"No configuration for {app_name} in {env_name}")
            return False
        
        deploy_dir = self.deployments_dir / app_name /env_name
        print(f"deploy dir before create: {deploy_dir}")
        
        deploy_dir.mkdir(parents=True, exist_ok=True)
        print(f"deploy dir after create: {deploy_dir}")
        
        try:
            self._copy_app_files(app_path, deploy_dir)
            if config.get("needs_venv", False):
                self._setup_venv(deploy_dir)
                
            if config.get("startup_script"):
                self._run_startup_script(deploy_dir, config["startup_script"])
                
            print(f"Succesfully deployed {app_name} to {env_name}")
            return True
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            return False
        
    def _copy_app_files(self, source_path, deploy_dir):
        """Copy application files to deployment directory."""
        source_path = Path(source_path)
        
        
        for item in deploy_dir.glob("*"):
            if item.name != "venv":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        for item in source_path.glob("*"):
            if item.is_dir():
                shutil.copytree(item, deploy_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, deploy_dir / item.name)
            
        
    def _setup_venv(self, deploy_dir):
        """Setup virtual environment for application"""
        print("setting up vevn")
        venv_dir = deploy_dir / "venv"
        print(f"Virtual env dir: {venv_dir}")
        
        if not venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir) ])
            
        activate_script = venv_dir / "bin" / "activate"
        if not activate_script.exists():
            print(f"Warning: activate script not found at {activate_script}")
            
        pip_path = venv_dir / "bin" / "pip"
        if not pip_path.exists():
            print("Pip not found, installing")
            python_path = venv_dir / "bin" / "python"
            subprocess.run([str(python_path), "-m", "ensurepip", "--upgrade"])
            subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    
                
        req_file = deploy_dir / "requirements.txt"
        if req_file.exists():
            python_path = venv_dir / "bin" / "python"
            subprocess.run([str(python_path), "-m", "pip", "install", "-r", str(req_file)])
            
    def _run_startup_script(self, deploy_dir, script_name):
        script_path = deploy_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Startup script {script_name} not found")
        
        script_path.chmod(script_path.stat().st_mode | 0o111)
        
        subprocess.Popen([str(script_path)], cwd=str(deploy_dir))
        
        
        
                                                                                                                         