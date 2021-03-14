import enum


class MediaType(enum.Enum):
    MEDIA_TYPE_WILDCARD = '*'
    WILDCARD = '*/*'
    APPLICATION_XML = 'application/xml'
    APPLICATION_ATOM_XML = 'application/atom+xml'
    APPLICATION_XHTML_XML = 'application/xhtml+xml'
    APPLICATION_SVG_XML = 'application/svg+xml'
    APPLICATION_JSON = 'application/json'
    APPLICATION_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    MULTIPART_FORM_DATA = 'multipart/form-data'
    APPLICATION_OCTET_STREAM = 'application/octet-stream'
    TEXT_PLAIN = 'text/plain'
    TEXT_XML = 'text/xml'
    TEXT_HTML = 'text/html'
    SERVER_SENT_EVENTS = 'text/event-stream'
    APPLICATION_JSON_PATCH_JSON = 'application/json-patch+json'


class HttpMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    PUT = 'PUT'


class HttpHeaders(enum.Enum):
    ACCEPT = 'Accept'
    ACCEPT_CHARSET = 'Accept-Charset'
    ACCEPT_ENCODING = 'Accept-Encoding'
    ACCEPT_LANGUAGE = 'Accept-Language'
    ACCEPT_RANGERS = 'Accept-Ranges'
    ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
    ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
    ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
    ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
    ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
    ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age'
    ACCESS_CONTROL_REQUEST_HEADERS = 'Access-Control-Request-Headers'
    ACCESS_CONTROL_REQUEST_METHOD = 'Access-Control-Request-Method'
    ALLOW = 'Allow'
    AUTHORIZATION = 'Authorization'
    CACHE_CONTROL = 'Cache-Control'
    CONNECTION = 'Connection'
    CONTENT_ENCODING = 'Content-Encoding'
    CONTENT_DISPOSITION = 'Content-Disposition'
    CONTENT_LANGUAGE = 'Content-Language'
    CONTENT_LENGTH = 'Content-Length'
    CONTENT_LOCATION = 'Content-Location'
    CONTENT_RANGE = 'Content-Range'
    CONTENT_TYPE = 'Content-Type'


class TimeUnit(enum.Enum):
    SECOND = 101
    MINUTE = 102
    HOUR = 103
    DAY = 104
    WEEK = 105
    MONTH = 106
    YEAR = 107
