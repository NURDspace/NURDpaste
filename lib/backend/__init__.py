
import redis
import pathlib

from lib.log import LoggingClass # pyright: ignore

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6379

class RedisBackend(LoggingClass):
    _redis: redis.Redis

    _class_parameters: dict = {
        'host': str,
        'port': int,
        'logconfig_use': str,
        'logconfig_file': pathlib.Path,
    }

    def __init__(self, **kwargs):
        for kw in self._class_parameters:
            assert kw in kwargs
            assert type(kwargs[kw] == self._class_parameters[kw])
            match type(kwargs[kw]):
                case pathlib.Path():
                    assert kwargs[kw].exists()
                case str():
                    assert len(kwargs[kw]) > 0
                case int():
                    assert kwargs[kw] > 0

        assert kwargs['port'] in range(1024, 65536)

        self._redis = redis.Redis(host=kwargs['host'], port=kwargs['port'], decode_responses=True)

        LoggingClass.__init__(self,
            logconfig_use=kwargs['logconfig_use'],
            logconfig_file=kwargs['logconfig_file'],
        )

    def store(self, key, value, ttl, size):
        if not self._redis.setex(key, ttl, value):
            self.print_warning(f"Failed to write data to redis")

    def fetch(self, key):
        return self._redis.get(key)

    def delete(self, key):
        return self._redis.delete(key)
