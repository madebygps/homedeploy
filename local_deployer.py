import shutil
import subprocess
import sys
from pathlib import Path

class LocalDeployer:
    def __init__(self, config_manager, base_dir):
        self.config_manager = config_manager
        self.base_dir = Path(base_dir)
        self.deployments_dir = self.base_dir / "deployments"
        self.logs_dir = self.base_dir / "logs"
        self.deployments_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def deploy(self, app_name, app_path, env="dev"):
        """Deploy an app to the local NAS."""
        print(f"Deploying {app_name} to {env}")
        
        # Get app configuration
        config = self.config_manager.get_app_config(app_name, env)
        if not config:
            print(f"No configuration found for {app_name} in {env}")
            return False
        
        # Create deployment directory
        deploy_dir = self.deployments_dir / app_name / env
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy application files
            self._copy_app_files(app_path, deploy_dir)
            
            # Create virtual environment if needed
            if config.get("needs_venv", False):
                self._setup_venv(deploy_dir)
            
            # Run startup script if it exists
            if config.get("startup_script"):
                self._run_startup_script(deploy_dir, config["startup_script"])
            
            print(f"Successfully deployed {app_name} to {env}")
            return True
            
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            return False
    
    def _copy_app_files(self, source_path, deploy_dir):
        """Copy application files to deployment directory."""
        source_path = Path(source_path)
        
        # Clear existing files (except venv if it exists)
        for item in deploy_dir.glob("*"):
            if item.name != "venv":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        # Copy new files
        for item in source_path.glob("*"):
            if item.is_dir():
                shutil.copytree(item, deploy_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, deploy_dir / item.name)
    
    def _setup_venv(self, deploy_dir):
        """Set up virtual environment for the application."""
        venv_dir = deploy_dir / "venv"
        
        # Create venv if it doesn't exist
        if not venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        
        # Install requirements if present
        req_file = deploy_dir / "requirements.txt"
        if req_file.exists():
            pip_path = venv_dir / "bin" / "pip"
            subprocess.run([str(pip_path), "install", "-r", str(req_file)])
    
    def _run_startup_script(self, deploy_dir, script_name):
        """Run the application startup script."""
        script_path = deploy_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Startup script {script_name} not found")
        
        # Make script executable
        script_path.chmod(script_path.stat().st_mode | 0o111)
        
        # Run the script
        subprocess.Popen([str(script_path)], cwd=str(deploy_dir))