from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ApiError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def api_exception_handler(exc, context):
    if isinstance(exc, ApiError):
        return Response(
            {
                'success': False,
                'statusCode': exc.status_code,
                'message': exc.message,
            },
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return Response(
            {
                'success': False,
                'statusCode': response.status_code,
                'message': response.data.get('detail', str(exc)) if isinstance(response.data, dict) else str(exc),
            },
            status=response.status_code,
        )

    return Response(
        {
            'success': False,
            'statusCode': 500,
            'message': str(exc) or 'Internal Server Error',
        },
        status=500,
    )


def set_auth_cookie(response, token, max_age):
    from django.conf import settings

    response.set_cookie(
        key='access_token',
        value=token,
        max_age=max_age,
        samesite=settings.COOKIE_OPTIONS['samesite'],
        httponly=settings.COOKIE_OPTIONS['httponly'],
        secure=settings.COOKIE_OPTIONS['secure'],
    )
    return response
