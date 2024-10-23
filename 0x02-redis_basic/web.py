#!/usr/bin/env python3
"""
Module for fetching web pages with Redis caching and access counting.
Implements caching of web pages with expiration and tracks access frequency.
"""

import redis
import requests
import functools
from typing import Callable


def url_count(method: Callable) -> Callable:
    """
    Decorator to track the number of times a URL is accessed.
    
    Args:
        method: The method to be decorated
        
    Returns:
        Callable: The wrapped method that includes URL access counting
    """
    @functools.wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that increments the URL access counter and calls the method.
        
        Args:
            url: The URL to fetch
            
        Returns:
            str: The page content
        """
        redis_client = redis.Redis()
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper


def cache_page(expiration: int = 10) -> Callable:
    """
    Decorator to cache the page content with expiration.
    
    Args:
        expiration: Cache expiration time in seconds (default: 10)
        
    Returns:
        Callable: The wrapped method that includes page content caching
    """
    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(url: str) -> str:
            """
            Wrapper function that implements page caching and calls the method.
            
            Args:
                url: The URL to fetch
                
            Returns:
                str: The page content (from cache if available)
            """
            redis_client = redis.Redis()
            cache_key = f"cache:{url}"
            
            # Try to get content from cache
            cached_content = redis_client.get(cache_key)
            if cached_content is not None:
                return cached_content.decode('utf-8')
            
            # If not in cache, fetch and store
            content = method(url)
            redis_client.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator


@url_count
@cache_page(10)
def get_page(url: str) -> str:
    """
    Obtain the HTML content of a URL with caching and access counting.
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The HTML content of the page
        
    Note:
        - Results are cached for 10 seconds
        - Number of access attempts is tracked
        - Uses Redis for caching and counting
    """
    response = requests.get(url)
    return response.text
