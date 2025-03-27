import os
import argparse
from .config.parser import parse_nl_config
from .core.local import LocalDeployer

def create_parser():
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(
        description="HomeDeploy: Natural language deployment tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python -m homedeploy deploy config.txt
  python -m homedeploy validate config.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy based on config")
    deploy_parser.add_argument("config", help="Path to natural language config file")
    deploy_parser.add_argument("-d", "--dry-run", action="store_true", 
                             help="Validate but don't actually deploy")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate config without deploying")
    validate_parser.add_argument("config", help="Path to natural language config file")
    
    return parser

def run_cli():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file '{args.config}' not found")
        return 1
    
    # Read config file
    with open(args.config, 'r') as f:
        config_text = f.read()
    
    # Parse natural language config
    print("Parsing config...")
    try:
        config = parse_nl_config(config_text)
        print(f"✓ Parsed configuration for: {config.name}")
    except Exception as e:
        print(f"✗ Error parsing config: {e}")
        return 1
    
    # Display config details
    print(f"\nConfiguration details:")
    print(f"  Name: {config.name}")
    print(f"  Source: {config.source_path}")
    print(f"  Target: {config.target_path}")
    if config.backup_path:
        print(f"  Backup: {config.backup_path}")
    if config.restart_service:
        print(f"  Service: {config.restart_service}")
    if config.pre_deploy_commands:
        print(f"  Pre-deploy commands: {len(config.pre_deploy_commands)}")
    if config.post_deploy_commands:
        print(f"  Post-deploy commands: {len(config.post_deploy_commands)}")
    print("")
    
    # Handle commands
    if args.command == "validate":
        print("✓ Config is valid")
        return 0
    
    elif args.command == "deploy":
        if args.dry_run:
            print("Dry run - deployment would succeed with this config")
            return 0
            
        # Execute deployment
        deployer = LocalDeployer(config)
        result = deployer.deploy()
        
        return 0 if result else 1