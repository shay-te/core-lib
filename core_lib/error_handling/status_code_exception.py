class StatusCodeException(Exception):
    def __init__(self, status_code: int, *args, **kwargs):
        self.status_code = status_code
        super(StatusCodeException, self).__init__(*args, **kwargs)
