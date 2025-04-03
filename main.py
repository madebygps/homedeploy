from ollama import chat
from pydantic import BaseModel

from models import DeploymentConfig

# Import your models from above

response = chat(
    messages=[
        {
            'role': 'user',
            'content': 'Deploy a FastAPI application called CustomerAPI using Python 3.9. It needs 1 CPU and 2GB of memory. Map port 8000 to 8080. Use a volume from /mnt/nas/data to /app/data. Set DATABASE_URL environment to postgresql://user:pass@db:5432/db. Deploy to TrueNAS.',
        }
    ],
    model='llama3.2',
    format=DeploymentConfig.model_json_schema(),
)

config = DeploymentConfig.model_validate_json(response.message.content)
print(config)