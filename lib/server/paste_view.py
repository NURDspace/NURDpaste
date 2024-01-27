import base64
import filetype
import json
import secrets

from cryptography.fernet import Fernet
from flask import request, redirect
from flask.views import MethodView

from lib.backend import RedisBackend # pyright: ignore

class PasteView(MethodView):
    init_every_request = False
    _backend: RedisBackend
    _fernet: Fernet
    _max_size: int
    _default_ttl: int

    def __init__(self, parent):
        self._parent = parent
        self._fernet = parent._fernet
        self._backend = parent._backend
        self._max_size = parent._max_size
        self._default_ttl = parent._default_ttl

    def print_info(self, *args, **kwargs) -> None:
        self._parent.print_info(*args, **kwargs)

    def print_warning(self, *args, **kwargs) -> None:
        self._parent.print_warning(*args, **kwargs)

    def post(self):
        size = len(request.get_data())
        if size > self._max_size:
            message = 'Uploaded data exceeds maximum allowed'
            self.print_warning(message)
            return message, 400

        raw_data = request.get_data()
        data = base64.b64encode(raw_data).decode('utf-8', 'strict')

        mime_type = filetype.guess_mime(raw_data)
        if mime_type == None:
            mime_type = 'text/plain'

        raw_storage_object = {
            'data': data,
            'mime_type': mime_type,
        }

        index = secrets.token_urlsafe()
        storage_object = self._fernet.encrypt(json.dumps(raw_storage_object).encode('utf-8'))
        object_url = f"{request.url_root}{index}"

        self._backend.store(index, storage_object, self._default_ttl, size)

        self.print_info(f"Stored {size} bytes worth of {mime_type} as {object_url} for {self._default_ttl} seconds")

        if 'Origin' in request.headers:
            return redirect(object_url)

        return f"{object_url}\n"
