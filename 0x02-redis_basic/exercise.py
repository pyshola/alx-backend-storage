#!/usr/bin/env python3
"""Module declares a redis class and methods"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''count how many times methods of Cache class are called'''
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''wrap the decorated function and return the wrapper'''
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''store the history of inputs and outputs for a particular function'''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''wrap the decorated function and return the wrapper'''
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper


class Cache:
    '''declares a Cache redis class'''
    def __init__(self):
        '''upon init to store an instance and flush'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''takes a data argument and returns a string'''
        rkey = str(uuid4())
        self._redis.set(rkey, data)
        return rkey