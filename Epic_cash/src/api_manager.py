from .binary_api import BINARY_API
from .http_api import HTTP_APIv2

class API:
    binary: BINARY_API = None
    http: HTTP_APIv2 = None

    def load_settings(self, binary_path=None, settings=None):
        if binary_path:
            if not self.binary:
                self.binary = BINARY_API(binary_path=binary_path)
            else:
                self.binary.load_binary_path(binary_path=binary_path)

        if settings:
            self.http = HTTP_APIv2(settings=settings)
            if not self.binary:
                self.binary = BINARY_API(settings=settings)
            else:
                self.binary.load_settings(settings=settings)