import ollama
import json
from .models.local import LocalDeployment

def parse_nl_config(config_text: str) -> LocalDeployment:
    """
    Parse natural language config into LocalDeployment model
    
    Args:
        config_text: Natural language description of deployment
        
    Returns:
        LocalDeployment configured based on natural language description
    """
    prompt = f"""
    Convert this natural language local deployment description into JSON:

    ```
    {config_text}
    ```

    Return a JSON object with these fields:
    - name: Unique name for this deployment
    - description: Optional description
    - source_path: Path to source files
    - target_path: Path where files will be deployed
    - backup_path: Optional path for backups
    - restart_service: Optional service to restart
    - use_symlinks: Boolean, default false
    - pre_deploy_commands: List of commands to run before deployment
    - post_deploy_commands: List of commands to run after deployment

    Return ONLY the JSON without explanations.
    """
    
    try:
        # Call Ollama for structured data extraction
        response = ollama.chat(
            model="mistral:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract JSON from response
        response_text = response['message']['content']
        json_str = response_text.strip()
        
        # Handle code blocks if present
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].strip()
        
        # Convert to LocalDeployment
        config_dict = json.loads(json_str)
        return LocalDeployment(**config_dict)
    
    except Exception as e:
        print(f"Error parsing config: {e}")
        # Return a minimal valid config as fallback
        return LocalDeployment(
            name="error_config",
            source_path="",
            target_path=""
        )