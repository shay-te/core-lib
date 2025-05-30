from core_lib.error_handling.client_messages import ClientMessage
from core_lib.error_handling.status_code_exception import StatusCodeException


class StatusCodeClientMessageException(StatusCodeException):
    """
    An exception intended for client-facing errors, ensuring only predefined, safe messages
    are exposed via a ClientMessage enum. Includes an error code and a status code.
    """
    def __init__(self, client_message: ClientMessage, status_code: int = 400):
        if not isinstance(client_message, ClientMessage):
            raise ValueError("client_message must be a ClientMessage enum")

        self.client_message = client_message.message
        self.error_key = client_message.code
        self.full_error = f"{self.error_key}::{self.client_message}"

        super(StatusCodeClientMessageException, self).__init__(status_code, self.client_message)
