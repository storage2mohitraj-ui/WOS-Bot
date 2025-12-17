import os
import time
import logging
import asyncio
from typing import Optional
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError

_LOGGER = logging.getLogger(__name__)
_DEFAULT_URI = os.getenv('MONGO_URI')

# Global connection pool - reuse single client instance
_GLOBAL_CLIENT: Optional[MongoClient] = None
_CLIENT_LOCK = asyncio.Lock()


def _create_client(uri: str, connect_timeout_ms: int = 5000) -> MongoClient:
    """Create a new MongoClient with optimized settings for Render deployment.
    
    This is a synchronous function that should be called from async context
    using asyncio.to_thread() to avoid blocking the event loop.
    """
    # Connection pool settings optimized for Render
    client = MongoClient(
        uri,
        server_api=ServerApi('1'),
        # Connection timeouts
        serverSelectionTimeoutMS=connect_timeout_ms,
        connectTimeoutMS=connect_timeout_ms,
        socketTimeoutMS=20000,  # 20s socket timeout
        # Connection pooling
        maxPoolSize=10,  # Max 10 connections per host
        minPoolSize=1,   # Keep 1 connection alive
        maxIdleTimeMS=45000,  # Close idle connections after 45s
        # Retry settings
        retryWrites=True,
        retryReads=True,
    )
    
    # Verify connection works
    client.admin.command('ping')
    _LOGGER.info('Created new MongoDB client with connection pooling')
    return client


async def get_mongo_client(uri: str | None = None, *, connect_timeout_ms: int | None = None) -> MongoClient:
    """Return a connected MongoClient with connection pooling.
    
    This async function reuses a global client instance to avoid repeated
    authentication overhead. The client is created in a thread pool to avoid
    blocking the asyncio event loop during the initial connection.
    
    Supports automatic fallback to MONGO_URI_FALLBACK if primary MONGO_URI fails.
    
    Raises ValueError if no URI is available or RuntimeError if connection fails.
    """
    global _GLOBAL_CLIENT
    
    uri = uri or _DEFAULT_URI
    fallback_uri = os.getenv('MONGO_URI_FALLBACK')
    
    if not uri:
        raise ValueError('No MongoDB URI provided. Set MONGO_URI in environment or pass uri param')
    
    # Default timeout (5s for faster failures on Render free tier)
    if connect_timeout_ms is None:
        try:
            connect_timeout_ms = int(os.getenv('MONGO_CONNECT_TIMEOUT_MS', '5000'))
        except Exception:
            connect_timeout_ms = 5000
    
    # Use global client if available and healthy
    async with _CLIENT_LOCK:
        if _GLOBAL_CLIENT is not None:
            try:
                # Quick health check in thread pool to avoid blocking
                await asyncio.to_thread(_GLOBAL_CLIENT.admin.command, 'ping')
                return _GLOBAL_CLIENT
            except Exception as e:
                _LOGGER.warning(f'Global MongoDB client unhealthy, recreating: {e}')
                try:
                    _GLOBAL_CLIENT.close()
                except Exception:
                    pass
                _GLOBAL_CLIENT = None
        
        # Try primary URI first, then fallback URI if available
        uris_to_try = [uri]
        if fallback_uri and fallback_uri != uri:
            uris_to_try.append(fallback_uri)
        
        for uri_index, current_uri in enumerate(uris_to_try):
            uri_label = "primary" if uri_index == 0 else "fallback"
            _LOGGER.info(f'Attempting to connect to {uri_label} MongoDB...')
            
            # Create new client with retries for this URI
            retries = 3
            last_exc: Exception | None = None
            
            for attempt in range(1, retries + 1):
                try:
                    _LOGGER.debug(f'Creating MongoDB client for {uri_label} URI (attempt {attempt}/{retries})')
                    # Run blocking connection in thread pool
                    client = await asyncio.to_thread(_create_client, current_uri, connect_timeout_ms)
                    _GLOBAL_CLIENT = client
                    _LOGGER.info(f'✅ Connected to {uri_label} MongoDB on attempt {attempt}/{retries}')
                    return client
                    
                except ServerSelectionTimeoutError as e:
                    last_exc = e
                    _LOGGER.warning(f'{uri_label.capitalize()} MongoDB connection attempt {attempt}/{retries} failed: {e}')
                    if attempt < retries:
                        backoff = 2 ** (attempt - 1)
                        _LOGGER.info(f'Waiting {backoff}s before retry')
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        _LOGGER.error(f'All {uri_label} MongoDB connection attempts failed')
                        # Don't raise here, try next URI if available
                        break
                        
                except PyMongoError as e:
                    last_exc = e
                    _LOGGER.exception(f'Unexpected PyMongo error on {uri_label} URI: {e}')
                    # Don't raise here, try next URI if available
                    break
            
            # If this was the last URI and we failed, raise error
            if uri_index == len(uris_to_try) - 1:
                _LOGGER.error(f'❌ All MongoDB URIs failed (tried {len(uris_to_try)} URI(s))')
                raise RuntimeError(f'Could not connect to any MongoDB URI after {retries} attempts: {last_exc}') from last_exc
        
        raise RuntimeError(f'Could not connect to MongoDB: {last_exc}')


async def close_mongo_client():
    """Close the global MongoDB client gracefully.
    
    Should be called during bot shutdown to clean up connections.
    """
    global _GLOBAL_CLIENT
    
    async with _CLIENT_LOCK:
        if _GLOBAL_CLIENT is not None:
            try:
                _LOGGER.info('Closing global MongoDB client')
                await asyncio.to_thread(_GLOBAL_CLIENT.close)
                _GLOBAL_CLIENT = None
                _LOGGER.info('MongoDB client closed successfully')
            except Exception as e:
                _LOGGER.error(f'Error closing MongoDB client: {e}')


# Backward compatibility: synchronous version for non-async contexts
_SYNC_CLIENT_LOCK = None  # Will be initialized as threading.Lock when needed

def get_mongo_client_sync(uri: str | None = None, *, connect_timeout_ms: int | None = None) -> MongoClient:
    """Synchronous version of get_mongo_client for backward compatibility.
    
    WARNING: This function blocks and should only be used in non-async contexts.
    Prefer the async version whenever possible.
    
    Now properly caches the global client to avoid creating new connections.
    Supports automatic fallback to MONGO_URI_FALLBACK if primary MONGO_URI fails.
    """
    global _GLOBAL_CLIENT, _SYNC_CLIENT_LOCK
    
    uri = uri or _DEFAULT_URI
    fallback_uri = os.getenv('MONGO_URI_FALLBACK')
    
    if not uri:
        raise ValueError('No MongoDB URI provided. Set MONGO_URI in environment or pass uri param')
    
    if connect_timeout_ms is None:
        try:
            connect_timeout_ms = int(os.getenv('MONGO_CONNECT_TIMEOUT_MS', '5000'))
        except Exception:
            connect_timeout_ms = 5000
    
    # Initialize threading lock if needed (for synchronous contexts)
    if _SYNC_CLIENT_LOCK is None:
        import threading
        _SYNC_CLIENT_LOCK = threading.Lock()
    
    # Thread-safe client reuse
    with _SYNC_CLIENT_LOCK:
        # If we have a global client, try to use it
        if _GLOBAL_CLIENT is not None:
            try:
                _GLOBAL_CLIENT.admin.command('ping')
                return _GLOBAL_CLIENT
            except Exception as e:
                _LOGGER.warning(f'Global MongoDB client unhealthy in sync context, recreating: {e}')
                try:
                    _GLOBAL_CLIENT.close()
                except Exception:
                    pass
                _GLOBAL_CLIENT = None
        
        # Try primary URI first, then fallback URI if available
        uris_to_try = [uri]
        if fallback_uri and fallback_uri != uri:
            uris_to_try.append(fallback_uri)
        
        last_exc: Exception | None = None
        
        for uri_index, current_uri in enumerate(uris_to_try):
            uri_label = "primary" if uri_index == 0 else "fallback"
            _LOGGER.info(f'Attempting to connect to {uri_label} MongoDB (sync)...')
            
            try:
                # Create new client and cache it globally
                _LOGGER.debug(f'Creating new MongoDB client for {uri_label} URI in sync context')
                client = _create_client(current_uri, connect_timeout_ms)
                _GLOBAL_CLIENT = client  # Cache the client globally
                _LOGGER.info(f'✅ Connected to {uri_label} MongoDB (sync)')
                return client
            except Exception as e:
                last_exc = e
                _LOGGER.warning(f'{uri_label.capitalize()} MongoDB connection failed (sync): {e}')
                # Try next URI if available
                continue
        
        # All URIs failed
        _LOGGER.error(f'❌ All MongoDB URIs failed in sync context (tried {len(uris_to_try)} URI(s))')
        raise RuntimeError(f'Could not connect to any MongoDB URI: {last_exc}') from last_exc


