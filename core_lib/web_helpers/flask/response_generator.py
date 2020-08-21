from flask import Flask
import json
from core_lib.web_helpers.constants_media_type import MediaType


def generate_response_flask(data, status):
    return Flask.response_class(response=json.dumps(data),
                                status=status,
                                mimetype=MediaType.APPLICATION_JSON.value)