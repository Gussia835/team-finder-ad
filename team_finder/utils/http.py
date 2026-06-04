import json
from http import HTTPStatus

from django.http import JsonResponse

from team_finder.constants import (JSON_KEY_ERROR,
                                   JSON_KEY_STATUS,
                                   JSON_STATUS_OK)


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return {}


def json_forbidden(message='Forbidden'):
    return JsonResponse({JSON_KEY_ERROR: message},
                        status=HTTPStatus.FORBIDDEN)


def json_bad_request(message):
    return JsonResponse({JSON_KEY_ERROR: message},
                        status=HTTPStatus.BAD_REQUEST)


def json_ok(extra=None, status=HTTPStatus.OK):
    data = {JSON_KEY_STATUS: JSON_STATUS_OK}
    if extra:
        data.update(extra)
    return JsonResponse(data, status=status)
