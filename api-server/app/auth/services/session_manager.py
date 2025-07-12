from datetime import datetime, UTC, timedelta
import jwt
import os
from ...singletons.logs_manager import LogsManager
from ..models.session_database_model import Session
from ..models.session_status_enum import SessionStatusEnum
from .token_manager import get_active_tokens_for_session
from .token_manager import create_token_for_session

logger = LogsManager().get_logger()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
MAX_TOKENS_PER_SESSION = int(os.getenv("MAX_TOKENS_PER_SESSION"))
SESSION_EXPIRES_IN = 86400 # 24 hours

async def create_session(token, user_id: str, x_exosphere_request_id: str):
    """Create a new session record for a token or update an existing one."""
    try:
        logger.info("Checking for existing session", x_exosphere_request_id=x_exosphere_request_id, user_id=user_id)
        existing_session = await get_active_session(user_id)

        # Get token expiration
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        expires_at = datetime.fromtimestamp(decoded["exp"], UTC)

        if expires_at < datetime.now(UTC):
            logger.error("Token is expired", x_exosphere_request_id=x_exosphere_request_id, user_id=user_id)
            return None

        # If an existing session is found, update it with the new token
        if existing_session:
            logger.info("Active session found, updating with new token.", x_exosphere_request_id=x_exosphere_request_id, user_id=user_id)
            await update_existing_session(token, existing_session, x_exosphere_request_id)
            return existing_session
        else:
            logger.info("No active session found, creating new session.", x_exosphere_request_id=x_exosphere_request_id)
            session_expires_at = datetime.now(UTC) + timedelta(seconds=SESSION_EXPIRES_IN)
            # Save session to database
            new_session = Session.create_new_session(user_id, session_expires_at)
            await new_session.insert()
            logger.info("New session created", x_exosphere_request_id=x_exosphere_request_id, user_id=user_id)
            return new_session

    except ValueError as ve:
        logger.error("Value error in session creation", error=str(ve), x_exosphere_request_id=x_exosphere_request_id, exc_info=True)
        raise ve
    except Exception as e:
        logger.error("Failed to create or update session", error=str(e), x_exosphere_request_id=x_exosphere_request_id, exc_info=True)
        raise e


async def get_active_session(user_id: str):
    """Get all active sessions for a user"""
    current_time = datetime.now(UTC)
    # Use a dictionary format for query conditions
    query = {
        "user_id": user_id,
        "expires_at": {"$gt": current_time},
        "session_status": SessionStatusEnum.ACTIVE
    }
    session = await Session.find_one(query)
    if not session:
        logger.info("No active session found for user", user_id=user_id)
        return None
    return session

async def end_session(session_id: str):
    """Remove a session from active sessions"""
    session = await Session.find_one({"session_id": session_id})
    if session:
        session.status = SessionStatusEnum.INACTIVE
        await session.save()
        return True
    return False

async def update_session_activity(session_id: str):
    """Update the last activity timestamp of a session"""
    session = await Session.find_one({"session_id": session_id})
    if session:
        session.last_activity = datetime.now(UTC)
        await session.save()
        return True
    return False

async def update_existing_session(token: str, existing_session: Session, x_exosphere_request_id: str):
    """Update an existing session with a new token"""

    # Count existing active tokens for this session
    active_tokens = await get_active_tokens_for_session(str(existing_session.id))

    if len(active_tokens) >= MAX_TOKENS_PER_SESSION:
        logger.warning("Maximum tokens reached for session", x_exosphere_request_id=x_exosphere_request_id,user_id=existing_session.user_id)
        raise ValueError(f"Maximum tokens per session limit reached ({MAX_TOKENS_PER_SESSION}). Cannot add more tokens to this session.")

    # Update session's last activity
    existing_session.last_activity = datetime.now(UTC)
    await existing_session.save()

    logger.info("Existing session updated", x_exosphere_request_id=x_exosphere_request_id,user_id=existing_session.user_id)
    return existing_session