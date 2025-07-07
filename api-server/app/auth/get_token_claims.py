import jwt
import os
import time

from app.singletons.logs_manager import LogsManager

from .models.token_claims import TokenClaims

logger = LogsManager().get_logger()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set or is empty.")
JWT_ALGORITHM = "HS256"


async def get_token_claims(token: str, x_exosphere_request_id: str):
    try:
        claims = TokenClaims(**jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]))
        logger.info("Token claims decoded", x_exosphere_request_id=x_exosphere_request_id, user_id=claims.user_id)
        
        if claims.exp < time.time():
            logger.error("Token expired", x_exosphere_request_id=x_exosphere_request_id, user_id=claims.user_id)
            return None
        
        return claims

    except Exception as e:
        logger.error("Error decoding token", error=e, x_exosphere_request_id=x_exosphere_request_id)
        return None
    