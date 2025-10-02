"""
CORS configuration for the State Manager API
"""
import os
from typing import List

def get_cors_origins() -> List[str]:
    """
    Get CORS origins from environment variables or use defaults
    """
    # Get origins from environment variable
    cors_origins = os.getenv("CORS_ORIGINS", "")
    
    if cors_origins:
        # Split by comma and strip whitespace
        return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    
    # Default origins for development
    return [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:3001",  # Alternative frontend port
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:3001",  # Alternative localhost port
    ]

def get_cors_config():
    """
    Get CORS configuration
    """
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "X-API-Key",
            "Authorization",
            "X-Requested-With",
            "X-Exosphere-Request-ID",
        ],
        "expose_headers": [  
            "X-Exosphere-Request-ID",  
        ],
    }
