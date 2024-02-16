import ipaddress
import pathlib

from cryptography.fernet import Fernet

from lib.log import LoggingClass # pyright: ignore
from lib.backend import RedisBackend # pyright: ignore
from lib.server.fetch_view import FetchView # pyright: ignore
from lib.server.paste_view import PasteView # pyright: ignore

from flask import Flask, render_template, render_template_string
app = Flask('nurdpaste-api')

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 9000
DEFAULT_MAX_SIZE = 33554432 # 32MB

class NURDpasteAPI(LoggingClass):
    _bind_ip: str = DEFAULT_IP
    _bind_port: int = DEFAULT_PORT
    _max_size: int = DEFAULT_MAX_SIZE
    _frontend: str
    _base_url: str
    _backend: RedisBackend
    _fernet: Fernet

    _nurdpaste_api_parameters: dict = {
        'bind_ip': str,
        'bind_port': int,
        'max_size': int,
        'default_ttl': int,
        'logconfig_use': str,
        'logconfig_file': pathlib.Path,
        'frontend': pathlib.Path,
        'base_url': str,
        'backend': RedisBackend,
    }

    def __init__(self, **kwargs):
        for kw in self._nurdpaste_api_parameters:
            assert kw in kwargs
            assert type(kwargs[kw] == self._nurdpaste_api_parameters[kw])
            match type(kwargs[kw]):
                case pathlib.Path():
                    assert kwargs[kw].exists()
                case str():
                    assert len(kwargs[kw]) > 0
                case int():
                    assert kwargs[kw] > 0
                case RedisBackend():
                    assert kwargs[kw] != None

        assert type(ipaddress.ip_address(kwargs['bind_ip'])) in [ipaddress.IPv4Address, ipaddress.IPv6Address]
        assert kwargs['bind_port'] in range(1024, 65536)

        self._bind_ip = kwargs['bind_ip']
        self._bind_port = kwargs['bind_port']
        self._max_size = kwargs['max_size']
        self._default_ttl = kwargs['default_ttl']
        self._frontend = kwargs['frontend']
        self._base_url = kwargs['base_url']
        self._backend = kwargs['backend']

        LoggingClass.__init__(self,
            logconfig_use=kwargs['logconfig_use'],
            logconfig_file=kwargs['logconfig_file'],
        )

        self._fernet = Fernet(Fernet.generate_key())

        paste_view = PasteView.as_view('paste_view', self)
        app.add_url_rule('/', methods=['POST'], view_func=paste_view)

        fetch_view = FetchView.as_view('fetch_view', self)
        app.add_url_rule('/<index>', methods=['GET'], view_func=fetch_view)

        app.add_url_rule('/', methods=['GET'], view_func=self.frontend)

    def frontend(self):
        with app.app_context():
            content = open(self._frontend, 'r').read()
            frontend = render_template_string(content,
                title="NURDpaste",
                max_size=self._max_size,
                ttl=self._default_ttl                                    
            )
        return frontend

    def run(self):
        app.run(
            host=self._bind_ip,
            port=self._bind_port,
        )
