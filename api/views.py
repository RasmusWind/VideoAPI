import os
import mimetypes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .base_serializers import UserSerializer, VideoSerializer, CategorySerializer
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from wsgiref.util import FileWrapper
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .utils import findNextRandomVid, RangeFileWrapper, range_re
from base.models import Video, Category


header_param = openapi.Parameter(
    "Authorization",
    openapi.IN_HEADER,
    description="Format: 'Token ...token...'",
    type=openapi.IN_HEADER,
)

login_param = {
    "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username "),
    "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password "),
}


@swagger_auto_schema(
    method="post",
    manual_parameters=[header_param],
)
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_video(request):
    serializer = VideoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response({"video": serializer.data})


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties=login_param),
)
@api_view(["POST"])
def rest_signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data.get("username"))
        user.set_password(request.data.get("password"))
        user.save()
        token = Token.objects.create(user=user)
        serializer = UserSerializer(instance=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties=login_param),
)
@api_view(["POST"])
def rest_login(request):
    user = get_object_or_404(User, username=request.data.get("username"))
    if not user.check_password(request.data.get("password")):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(instance=user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": serializer.data})


@swagger_auto_schema(method="get", manual_parameters=[header_param])
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rest_test_token(request):
    return Response(f"Success for user: {request.user.username}")


@swagger_auto_schema(method="get", manual_parameters=[header_param])
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rest_get_user(request):
    serializer = UserSerializer(instance=request.user)
    return Response({"user": serializer.data})


@swagger_auto_schema(method="post", manual_parameters=[header_param])
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_new_video(request):
    currentVidPath = request.user.profile.last_viewed
    path = "media/video_uploads"
    if not currentVidPath:
        newVidPath = "2024/01/24/video.mp4"
    else:
        newVidPath = findNextRandomVid(currentVidPath)
    path = f"{path}/{newVidPath}"
    print(path)
    request.user.profile.last_viewed = newVidPath
    request.user.profile.save()
    return Response({"status": "success"})


@swagger_auto_schema(method="get", manual_parameters=[header_param])
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def videoplayer(request):
    video_path = request.user.profile.last_viewed
    if not video_path:
        video_path = "2024/01/24/video.mp4"
    path = f"media/video_uploads/{video_path}"

    chunk_size = 2 * 1024 * 1024  # 2 MB

    range_header = request.META.get("HTTP_RANGE", "").strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or "application/octet-stream"
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        lb = first_byte + chunk_size
        if lb >= size:
            lb = size - 1
        last_byte = int(last_byte) if last_byte else lb
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(
            RangeFileWrapper(open(path, "rb"), offset=first_byte, length=length),
            status=206,
            content_type=content_type,
        )
        resp["Content-Length"] = str(length)
        resp["Content-Range"] = "bytes %s-%s/%s" % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(
            FileWrapper(open(path, "rb")), content_type=content_type
        )
        resp["Content-Length"] = str(size)
    resp["Accept-Ranges"] = "bytes"
    return resp


@swagger_auto_schema(
    method="get",
    manual_parameters=[header_param],
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    serializer = VideoSerializer(instance=video)
    return Response({"video": serializer.data})


@swagger_auto_schema(
    method="get",
    manual_parameters=[header_param],
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(instance=category)
    return Response({"video": serializer.data})
