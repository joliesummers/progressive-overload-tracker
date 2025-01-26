from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # AWS Settings
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    agent_id: str = os.getenv("BEDROCK_AGENT_ID", "")
    agent_alias_id: str = os.getenv("BEDROCK_AGENT_ALIAS_ID", "")

    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/workout_tracker")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
