from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def auth_check(func):
    def wrapper(request):
        if request.user and request.user.is_authenticated:
            return func(request)
        else:
            return JsonResponse(
                {"status": ("error", "User is not authenticated")}, safe=False
            )

    return wrapper


header_param = openapi.Parameter(
    "Authorization",
    openapi.IN_HEADER,
    description="Format: 'Token ...token...'",
    type=openapi.IN_HEADER,
)


@swagger_auto_schema(method="get", manual_parameters=[header_param])
def GET_authorization_header(func):
    def wrapper(request):
        return func(request)

    return wrapper
