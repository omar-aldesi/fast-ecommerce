import os
from aiocache import caches
from dotenv import load_dotenv
from app.core import logger
from fastapi.exceptions import HTTPException
from app.core.constants import REFRESH_TOKEN_BLACKLIST_PREFIX

load_dotenv()


# Store access token
async def store_access_token(token: str, user_id: int):
    cache = caches.get('default')
    await cache.set(f"access_token_{user_id}", token, ttl=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')))
    logger.info(f"Access token stored for user {user_id}")


# Get access token

async def get_access_token(user_id: int):
    cache = caches.get('default')
    try:
        return await cache.get(f"access_token_{user_id}", None)
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def add_refresh_token_to_blacklist(user_id: int, refresh_token: str):
    try:
        cache = caches.get('default')
        key = f"{REFRESH_TOKEN_BLACKLIST_PREFIX}{user_id}"
        tokens = await cache.get(key, default=[])
        tokens.append(refresh_token)
        ttl = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS', 1)) * 24 * 60 * 60  # Convert days to seconds
        await cache.set(key, list(tokens), ttl=ttl)
        logger.info(f"Refresh token added to blacklist for user {user_id}")
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def check_refresh_token(user_id: int, refresh_token: str) -> bool:
    try:
        cache = caches.get('default')
        key = f"{REFRESH_TOKEN_BLACKLIST_PREFIX}{user_id}"
        tokens = await cache.get(key, default=[])
        return refresh_token in tokens
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
