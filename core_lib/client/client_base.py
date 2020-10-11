import requests


class ClientBase(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = None
        self.timeout = None

    def set_headers(self, headers: dict):
        self.headers = headers

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def _get(self, path: str, *args, **kwargs):
        return self.session.get(self.__build_url(path), timeout=self.timeout, *args, **self.process_kwargs(**kwargs))

    def _put(self, path: str, *args, **kwargs):
        return self.session.put(self.__build_url(path), timeout=self.timeout, *args, **self.process_kwargs(**kwargs))

    def _post(self, path: str, *args, **kwargs):
        return self.session.post(self.__build_url(path), timeout=self.timeout, *args, **self.process_kwargs(**kwargs))

    def _delete(self, path: str, *args, **kwargs):
        return self.session.delete(self.__build_url(path), timeout=self.timeout, *args, **self.process_kwargs(**kwargs))

    def __build_url(self, path):
        return "{}/{}".format(self.base_url.rstrip("/"), path.lstrip("/"))

    def process_kwargs(self, **kwargs):
        if self.headers:
            if 'headers' in kwargs:
                kwargs['headers'] = {**kwargs['headers'], **self.headers}
            else:
                kwargs['headers'] = self.headers
        return kwargs
