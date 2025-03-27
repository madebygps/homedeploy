import os
import shutil
import subprocess
from datetime import datetime
from ..config.models import LocalDeployment

class LocalDeployer:
    """Handles local deployment operations"""
    
    def __init__(self, config: LocalDeployment):
        self.config = config
        
    def run_commands(self, commands: list) -> bool:
        """Run a list of shell commands"""
        if not commands:
            return True
            
        print(f"Running commands...")
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, check=True, 
                                       capture_output=True, text=True)
                print(f"✓ {cmd}")
                if result.stdout.strip():
                    print(f"  Output: {result.stdout.strip()}")
            except subprocess.CalledProcessError as e:
                print(f"✗ {cmd}")
                print(f"  Error: {e.stderr}")
                return False
        return True
        
    def backup(self) -> bool:
        """Create a backup if backup_path is specified"""
        if not self.config.backup_path:
            print("No backup path specified, skipping backup")
            return True
            
        # Create dated backup folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(
            self.config.backup_path, 
            f"{self.config.name}_{timestamp}"
        )
        
        try:
            if os.path.exists(self.config.target_path):
                print(f"Creating backup at {backup_dir}")
                os.makedirs(os.path.dirname(backup_dir), exist_ok=True)
                shutil.copytree(self.config.target_path, backup_dir)
                print(f"✓ Backup created")
            else:
                print(f"Target path doesn't exist yet, no backup needed")
            return True
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return False
    
    def deploy_files(self) -> bool:
        """Copy or symlink files to target location"""
        try:
            # Create target directory if needed
            target_dir = (self.config.target_path if os.path.isdir(self.config.source_path) 
                         else os.path.dirname(self.config.target_path))
            os.makedirs(target_dir, exist_ok=True)
            
            # Remove existing files if present
            if os.path.exists(self.config.target_path):
                if os.path.isdir(self.config.target_path):
                    shutil.rmtree(self.config.target_path)
                else:
                    os.remove(self.config.target_path)
            
            # Deploy files using copy or symlink
            if self.config.use_symlinks:
                print(f"Creating symlink from {self.config.source_path} to {self.config.target_path}")
                os.symlink(
                    os.path.abspath(self.config.source_path), 
                    self.config.target_path,
                    target_is_directory=os.path.isdir(self.config.source_path)
                )
            else:
                print(f"Copying files from {self.config.source_path} to {self.config.target_path}")
                if os.path.isdir(self.config.source_path):
                    shutil.copytree(self.config.source_path, self.config.target_path)
                else:
                    shutil.copy2(self.config.source_path, self.config.target_path)
            
            print(f"✓ Files deployed successfully")
            return True
        except Exception as e:
            print(f"✗ Deployment failed: {e}")
            return False
            
    def restart_services(self) -> bool:
        """Restart services if specified"""
        if not self.config.restart_service:
            return True
            
        restart_cmd = f"systemctl restart {self.config.restart_service}"
        try:
            print(f"Restarting service: {self.config.restart_service}")
            subprocess.run(restart_cmd, shell=True, check=True)
            print(f"✓ Service restarted")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Service restart failed: {e}")
            return False
    
    def deploy(self) -> bool:
        """Execute deployment based on config"""
        print(f"\n=== Starting deployment: {self.config.name} ===")
        if self.config.description:
            print(f"Description: {self.config.description}")
        print("")
        
        # Run pre-deploy commands
        if not self.run_commands(self.config.pre_deploy_commands):
            print("❌ Deployment failed: pre-deploy commands failed")
            return False
            
        # Backup existing deployment
        if not self.backup():
            print("❌ Deployment failed: backup failed")
            return False
        
        # Deploy files
        if not self.deploy_files():
            print("❌ Deployment failed: file deployment failed")
            return False
            
        # Restart services
        if not self.restart_services():
            print("❌ Deployment failed: service restart failed")
            return False
            
        # Run post-deploy commands
        if not self.run_commands(self.config.post_deploy_commands):
            print("❌ Deployment failed: post-deploy commands failed")
            return False
            
        print("\n✅ Deployment completed successfully!")
        return True