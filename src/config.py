from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    model_name: str = Field(default="gemini-2.0-flash-exp")
    temperature: float = Field(default=0.7)
    max_token_limit: int = Field(default=1000)

    # Mongo settings
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db: str = Field(default="agentic_bot")
    mongo_collection: str = Field(default="chat_logs")

    class Config:
        env_file = ".env"  


settings = Settings()
