#!/usr/bin/env python3
"""
This module implements a Cache class using Redis for storage.
It provides functionality to store and retrieve data with call counting
and history tracking capabilities.
"""

import redis
import uuid
import functools
from typing import Union, Callable, Optional, Any


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    
    Args:
        method: The method to be decorated
        
    Returns:
        Callable: The wrapped method that includes call counting
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the call counter and calls the method.
        
        Returns:
            The result of the original method
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    
    Args:
        method: The method to be decorated
        
    Returns:
        Callable: The wrapped method that tracks input/output history
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs in Redis lists.
        
        Returns:
            The result of the original method
        """
        # Create input and output list keys
        input_list_key = f"{method.__qualname__}:inputs"
        output_list_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(input_list_key, str(args))
        
        # Execute the method and store its output
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list_key, str(output))
        
        return output
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls for a particular function.
    
    Args:
        method: The method whose call history to display
    """
    # Get the Redis instance from the method's class
    redis_instance = method.__self__._redis
    method_name = method.__qualname__
    
    # Get the number of calls
    calls_count = int(redis_instance.get(method_name) or 0)
    
    # Print method name and number of calls
    print(f"{method_name} was called {calls_count} times:")
    
    # Get inputs and outputs
    inputs = redis_instance.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{method_name}:outputs", 0, -1)
    
    # Print each call with its input and output
    for input_args, output in zip(inputs, outputs):
        input_str = input_args.decode('utf-8')
        output_str = output.decode('utf-8')
        print(f"{method_name}(*{input_str}) -> {output_str}")


class Cache:
    """
    A cache class that implements a basic caching system using Redis.
    The class provides methods to store and retrieve data with type conversion support.
    """

    def __init__(self):
        """
        Initialize the Cache instance.
        Creates a Redis client instance and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis using a randomly generated key.

        Args:
            data: The data to be stored. Can be a str, bytes, int, or float.

        Returns:
            str: The randomly generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, 
            key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis storage using the provided key.
        Optionally convert the data using the provided conversion function.

        Args:
            key: The key under which the data is stored
            fn: Optional callable that will be used to convert the data

        Returns:
            The data in its original format, or None if the key doesn't exist
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieve a string value from Redis storage.
        Automatically converts bytes to utf-8 string.

        Args:
            key: The key under which the string is stored

        Returns:
            str: The stored string value, or None if the key doesn't exist
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieve an integer value from Redis storage.
        Automatically converts bytes to integer.

        Args:
            key: The key under which the integer is stored

        Returns:
            int: The stored integer value, or None if the key doesn't exist
        """
        return self.get(key, fn=int)
