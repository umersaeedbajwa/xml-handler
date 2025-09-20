"""
Cache utility similar to FusionPBX cache class
Provides abstracted cache functionality with file and memory methods
"""
import os
import json
import glob
import asyncio
from typing import Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, method: str = "file", location: str = "/var/cache/fusionpbx", syslog: bool = False):
        """
        Initialize cache with specified method
        
        Args:
            method: Cache method ('file' or 'memory')
            location: Cache directory location for file method
            syslog: Enable debug logging
        """
        self.method = method
        self.location = Path(location)
        self.syslog = syslog
        self.memory_cache = {} if method == "memory" else None
        
        # Ensure cache directory exists for file method
        if self.method == "file":
            self.location.mkdir(parents=True, exist_ok=True)
    
    def _log_debug(self, message: str):
        """Debug logging similar to FusionPBX syslog"""
        if self.syslog:
            logger.debug(f"cache: {message}")
    
    def _normalize_key(self, key: str) -> str:
        """Convert colon delimiters to dots like FusionPBX"""
        return key.replace(":", ".")
    
    async def set(self, key: str, value: Any) -> bool:
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            bool: Success status
        """
        try:
            normalized_key = self._normalize_key(key)
            
            if self.method == "file":
                cache_file = self.location / normalized_key
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert value to string if not already
                cache_value = json.dumps(value) if not isinstance(value, str) else value
                
                with open(cache_file, 'w') as f:
                    f.write(cache_value)
                
                self._log_debug(f"set file cache: {normalized_key}")
                return True
                
            elif self.method == "memory":
                self.memory_cache[normalized_key] = value
                self._log_debug(f"set memory cache: {normalized_key}")
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get cache value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            normalized_key = self._normalize_key(key)
            
            if self.method == "file":
                cache_file = self.location / normalized_key
                
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        content = f.read()
                    
                    # Try to parse as JSON, fallback to string
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
                        
                return None
                
            elif self.method == "memory":
                return self.memory_cache.get(normalized_key)
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete cache entry
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: Success status
        """
        try:
            normalized_key = self._normalize_key(key)
            
            self._log_debug(f"delete cache key: {normalized_key}")
            
            if self.method == "file":
                # Support wildcard deletion like FusionPBX
                cache_pattern = str(self.location / normalized_key)
                deleted_files = []
                
                for file_path in glob.glob(cache_pattern):
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                        deleted_files.append(file_path)
                    
                    # Also try to remove .tmp files
                    tmp_file = file_path + ".tmp"
                    if os.path.exists(tmp_file):
                        os.unlink(tmp_file)
                        deleted_files.append(tmp_file)
                
                self._log_debug(f"deleted files: {deleted_files}")
                return len(deleted_files) > 0
                
            elif self.method == "memory":
                if normalized_key in self.memory_cache:
                    del self.memory_cache[normalized_key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def flush(self) -> bool:
        """
        Flush entire cache
        
        Returns:
            bool: Success status
        """
        try:
            self._log_debug("flush all cache")
            
            if self.method == "file":
                # Remove all files in cache directory
                for file_path in self.location.rglob("*"):
                    if file_path.is_file():
                        os.unlink(file_path)
                
                return True
                
            elif self.method == "memory":
                self.memory_cache.clear()
                return True
                
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """
        Delete cache entries matching pattern
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            bool: Success status
        """
        try:
            normalized_pattern = self._normalize_key(pattern)
            
            if self.method == "file":
                cache_pattern = str(self.location / normalized_pattern)
                deleted_count = 0
                
                for file_path in glob.glob(cache_pattern):
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                        deleted_count += 1
                
                self._log_debug(f"deleted {deleted_count} files matching pattern: {normalized_pattern}")
                return deleted_count > 0
                
            elif self.method == "memory":
                import fnmatch
                keys_to_delete = [
                    key for key in self.memory_cache.keys() 
                    if fnmatch.fnmatch(key, normalized_pattern)
                ]
                
                for key in keys_to_delete:
                    del self.memory_cache[key]
                
                self._log_debug(f"deleted {len(keys_to_delete)} memory entries matching pattern: {normalized_pattern}")
                return len(keys_to_delete) > 0
                
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return False


# Global cache instance
cache_instance: Optional[Cache] = None


def get_cache() -> Cache:
    """Get global cache instance"""
    global cache_instance
    if cache_instance is None:
        # Default configuration - can be overridden
        cache_instance = Cache(method="file", location="/var/cache/fusionpbx", syslog=False)
    return cache_instance


def init_cache(method: str = "file", location: str = "/var/cache/fusionpbx", syslog: bool = False):
    """Initialize cache with configuration"""
    global cache_instance
    cache_instance = Cache(method=method, location=location, syslog=syslog)
    return cache_instance


async def invalidate_extension_cache(extension: str, user_context: str, number_alias: Optional[str] = None):
    """
    Invalidate extension-related cache entries
    Similar to FusionPBX cache clearing after extension updates
    
    Args:
        extension: Extension number
        user_context: User context (domain)
        number_alias: Optional number alias
    """
    cache = get_cache()
    
    # Cache keys that need to be cleared (following FusionPBX patterns)
    cache_keys = [
        f"directory:{extension}@{user_context}",
        f"extension:{extension}",
        f"user_context:{user_context}",
    ]
    
    if number_alias:
        cache_keys.append(f"directory:{number_alias}@{user_context}")
    
    # Clear all related cache entries
    for key in cache_keys:
        await cache.delete(key)
    
    logger.info(f"Invalidated cache for extension {extension}@{user_context}")


async def invalidate_domain_cache(domain_name: str):
    """
    Invalidate domain-related cache entries
    
    Args:
        domain_name: Domain name
    """
    cache = get_cache()
    
    # Clear domain-related cache patterns
    await cache.delete_pattern(f"*@{domain_name}")
    await cache.delete_pattern(f"domain:{domain_name}*")
    
    logger.info(f"Invalidated cache for domain {domain_name}")


async def invalidate_user_cache(username: str, domain_name: str):
    """
    Invalidate user-related cache entries
    
    Args:
        username: Username
        domain_name: Domain name
    """
    cache = get_cache()
    
    cache_keys = [
        f"user:{username}@{domain_name}",
        f"auth:{username}@{domain_name}",
    ]
    
    for key in cache_keys:
        await cache.delete(key)
    
    logger.info(f"Invalidated cache for user {username}@{domain_name}")

    