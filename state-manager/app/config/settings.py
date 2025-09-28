import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongo_uri: str = Field(..., description="MongoDB connection URI" )
    mongo_database_name: str = Field(default="exosphere-state-manager", description="MongoDB database name")
    state_manager_secret: str = Field(..., description="Secret key for API authentication")
    secrets_encryption_key: str = Field(..., description="Key for encrypting secrets")
    trigger_ahead_time: int = Field(default=10, description="Time in minutes to trigger the graph ahead of the current time")
    
    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mongo_uri=os.getenv("MONGO_URI"), # type: ignore
            mongo_database_name=os.getenv("MONGO_DATABASE_NAME", "exosphere-state-manager"), # type: ignore
            state_manager_secret=os.getenv("STATE_MANAGER_SECRET"), # type: ignore
            secrets_encryption_key=os.getenv("SECRETS_ENCRYPTION_KEY"), # type: ignore
            trigger_ahead_time=int(os.getenv("TRIGGER_AHEAD_TIME", 10)) # type: ignore
        )


# Global settings instance - will be updated when get_settings() is called
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance, reloading from environment if needed."""
    global _settings
    _settings = Settings.from_env()
    return _settings


# Initialize settings
settings = get_settings() 