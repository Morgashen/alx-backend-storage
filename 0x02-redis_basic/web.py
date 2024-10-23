#!/usr/bin/python3
import requests
import redis
from functools import wraps
import time

# Initialize Redis
cache = redis.Redis(host='localhost', port=6379, db=0)

# Decorator for caching with expiration time and tracking count
def cache_page(expire_time=10):
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            cache_key = f"content:{url}"
            count_key = f"count:{url}"
            
            # Check if the page is cached
            cached_content = cache.get(cache_key)
            if cached_content:
                print(f"Cache hit for {url}")
                return cached_content.decode('utf-8')
            
            # Otherwise, fetch the page and cache it
            print(f"Cache miss for {url}, fetching...")
            result = func(url)
            cache.setex(cache_key, expire_time, result)
            
            # Increment the count of access
            cache.incr(count_key)
            
            return result
        return wrapper
    return decorator

# The get_page function with caching and count tracking
@cache_page(expire_time=10)
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

# Test the function
if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk"
    print(get_page(test_url))
    time.sleep(5)
    print(get_page(test_url))
    time.sleep(12)
    print(get_page(test_url))  # This should re-fetch as cache expires after 10 seconds
