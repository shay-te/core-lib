import enum


class MediaType(enum.Enum):
    MEDIA_TYPE_WILDCARD = "*"
    WILDCARD = "*/*"
    APPLICATION_XML = "application/xml"
    APPLICATION_ATOM_XML = "application/atom+xml"
    APPLICATION_XHTML_XML = "application/xhtml+xml"
    APPLICATION_SVG_XML = "application/svg+xml"
    APPLICATION_JSON = "application/json"
    APPLICATION_FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA = "multipart/form-data"
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    TEXT_PLAIN = "text/plain"
    TEXT_XML = "text/xml"
    TEXT_HTML = "text/html"
    SERVER_SENT_EVENTS = "text/event-stream"
    APPLICATION_JSON_PATCH_JSON = "application/json-patch+json"
