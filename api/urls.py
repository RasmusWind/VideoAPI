from django.urls import path
from rest_framework.authtoken import views as authtoken_views
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponseRedirect


schema_view = get_schema_view(
    openapi.Info(
        title="Video API",
        default_version="v1",
        description="Test description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def swagger(request):
    return HttpResponseRedirect("/swagger")


urlpatterns = [
    path("", swagger),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # GET REQUEST PATHS:
    path("test_token", views.rest_test_token),
    path("streamvideo", views.videoplayer),
    path("get_user", views.rest_get_user),
    path("get_new_video", views.get_new_video),
    path("get_video/<int:pk>", views.get_video),
    path("get_category/<int:pk>", views.get_category),
    path("get_videocomments/<int:pk>", views.get_videocomments),
    # POST REQUEST PATHS:
    path("api-token-auth", authtoken_views.obtain_auth_token),
    path("login", views.rest_login),
    path("signup", views.rest_signup),
    path("uploadvideo", views.upload_video),
    path("setnewvideo", views.set_new_video),
    path("createcomment", views.create_comment),
]
