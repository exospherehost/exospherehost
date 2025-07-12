from datetime import datetime, timedelta, UTC
from typing import List
import hashlib
from ..models.token_database_model import Token
from ..models.token_status_enum import TokenStatusEnum

TOKEN_EXPIRATION_SECONDS = 3600  # Example: 1 hour

async def create_token_for_session(token: str, session_id: str, user_id: str) -> Token:
    token = Token(
        session_id=session_id,
        user_id=user_id,
        token =token,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(seconds=TOKEN_EXPIRATION_SECONDS)
    )
    await token.insert()
    return token

async def get_active_tokens_for_session(session_id: str) -> List[Token]:
    return await Token.find(
        Token.session_id == session_id,
        Token.status == TokenStatusEnum.ACTIVE
    ).to_list()

async def blacklist_token(token_id: str):
    token = await Token.find_one(Token.token_id == token_id)
    if token:
        token.status = TokenStatusEnum.BLACKLISTED
        await token.save()

async def get_active_tokens_for_user(user_id: str) -> List[Token]:
    """Get all active tokens for a user across all sessions"""
    return await Token.find(
        Token.user_id == user_id,
        Token.status == TokenStatusEnum.ACTIVE,
        Token.expires_at > datetime.now(UTC)
    ).to_list()