#!/usr/bin/env python3
import click
import os
from pathlib import Path

from config_manager import ConfigManager
from local_deployer import LocalDeployer

# Set up base directory
base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

@click.group()
def cli():
    """HomeDeploy: CLI tool to deploy to NAS or Azure."""
    pass

@cli.command()
@click.argument("app_name")
@click.argument("app_path")
@click.option("--env", "-e", default="dev", help="Environment (dev/stage/prod)")
def deploy_local(app_name, app_path, env):
    """Deploy an application to the local NAS."""
    config_manager = ConfigManager(base_dir)
    deployer = LocalDeployer(config_manager, base_dir)
    
    print(f"Deploying {app_name} to local NAS ({env})")
    success = deployer.deploy(app_name, app_path, env)
    
    if success:
        print("Deployment successful")
    else:
        print("Deployment failed")

@cli.command()
@click.argument("app_name")
def configure_app(app_name):
    """Create or update app configuration."""
    config_manager = ConfigManager(base_dir)
    config_manager.create_app_config(app_name)
    print(f"Configuration created for {app_name}")

@cli.command()
def list_deployments():
    """List all deployed applications."""
    deployments_dir = base_dir / "deployments"
    
    if not deployments_dir.exists() or not any(deployments_dir.iterdir()):
        print("No deployments found")
        return
    
    print("Deployed Applications:")
    
    for app_dir in deployments_dir.glob("*"):
        if app_dir.is_dir():
            app_name = app_dir.name
            print(f"{app_name}")
            
            for env_dir in app_dir.glob("*"):
                if env_dir.is_dir():
                    env_name = env_dir.name
                    print(f"  - {env_name}")

if __name__ == "__main__":
    # Create required directories
    (base_dir / "configs").mkdir(exist_ok=True)
    (base_dir / "deployments").mkdir(exist_ok=True)
    (base_dir / "logs").mkdir(exist_ok=True)
    
    cli()