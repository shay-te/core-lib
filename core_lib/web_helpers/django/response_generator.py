import json
from django.http import HttpResponse
from core_lib.helpers.constants import MediaType


def generate_response_django(data, status):
    content = json.dumps(data) if data else b''
    return HttpResponse(content=content, status=status, content_type=MediaType.APPLICATION_JSON.value)