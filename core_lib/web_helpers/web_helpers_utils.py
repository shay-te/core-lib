import enum


class WebHelpersUtils(object):

    server_type = None

    class ServerType(enum.Enum):
        FLASK = 'flask'
        DJANGO = 'django'

    @staticmethod
    def init(server_type: ServerType):
        # Every helper branches on this: anything else (a plain 'flask' string) would make them return None.
        if not isinstance(server_type, WebHelpersUtils.ServerType):
            raise ValueError(f'server_type must be a WebHelpersUtils.ServerType, got `{server_type!r}`')
        WebHelpersUtils.server_type = server_type

    @staticmethod
    def get_server_type() -> ServerType:
        if not WebHelpersUtils.server_type:
            raise ValueError('WebHelpersUtils never initialized')
        return WebHelpersUtils.server_type
