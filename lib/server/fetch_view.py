import base64
import json

from cryptography.fernet import Fernet, InvalidToken
from flask import request, Response
from flask.views import MethodView

from lib.backend import RedisBackend # pyright: ignore

class FetchView(MethodView):
    init_every_request = False
    _backend: RedisBackend
    _fernet: Fernet

    def __init__(self, parent):
        self._parent = parent
        self._fernet = parent._fernet
        self._backend = parent._backend

    def print_info(self, *args, **kwargs) -> None:
        self._parent.print_info(*args, **kwargs)

    def print_warning(self, *args, **kwargs) -> None:
        self._parent.print_warning(*args, **kwargs)

    def get(self, index=""):
        encrypted_object = self._backend.fetch(index)
        if not encrypted_object or len(encrypted_object) == 0:
            return "", 404
        
        try:
            storage_object = self._fernet.decrypt(encrypted_object)
        except InvalidToken:
            self.print_warning(f"Unable to decrypt object, deleting")
            self._backend.delete(index)
            return "", 404

        storage_object = json.loads(self._fernet.decrypt(encrypted_object))
        data = base64.urlsafe_b64decode(storage_object['data'])
        return Response(data, mimetype=storage_object['mime_type'])

