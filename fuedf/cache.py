#!/usr/bin/python
#encoding: utf-8

from functools import wraps

from flask import request

from werkzeug.contrib.cache import SimpleCache

CACHE_DEFAULT_TIMEOUT = 3600

_cache = SimpleCache()

# inspired by http://flask.pocoo.org/snippets/9/
# and http://flask.pocoo.org/docs/patterns/viewdecorators/#caching-decorator
class cached(object):
    def __init__(self, kind, timeout=None):
        self.kind = kind
        self.timeout = timeout or CACHE_DEFAULT_TIMEOUT

    def __call__(self, function):
        @wraps(function)
        def decorator(*args, **kwargs):
            if self.kind == 'data':
                what = function
            elif self.kind == 'view':
                what = request.url
            else:
                # no cache
                return function(*args, **kwargs)
            values = _cache.get(what)
            if values is None:
                values = function(*args, **kwargs)
                _cache.set(what, values, self.timeout)
            return values
        return decorator

    @staticmethod
    def clear():
        _cache.clear()

