class StatusCodeException(Exception):
    def __init__(self, status_code: int, message: str = '', *args, **kwargs):
        self.status_code = status_code
        self.message = message
        super(StatusCodeException, self).__init__(*args, **kwargs)
