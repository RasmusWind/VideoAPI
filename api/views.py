import os
import mimetypes
from django.contrib.auth import get_user_model, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .base_serializers import UserSerializer, VideoSerializer, CategorySerializer, CreateCommentSerializer, CommentSerializer, UserLoginSerializer
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from wsgiref.util import FileWrapper
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .utils import findNextRandomVid, RangeFileWrapper, range_re
from base.models import Video, Category, VideoComment

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
        print("PASSWORD WRONG")
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
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def set_new_video(request):
    currentVidPath = request.user.profile.last_viewed
    path = "media/video_uploads"
    if not currentVidPath:
        newVidPath = "video.mp4"
    else:
        newVidPath = findNextRandomVid(currentVidPath)

    if not newVidPath:
        newVidPath = "video.mp4"

    path = f"{path}/{newVidPath}"
    request.user.profile.last_viewed = newVidPath
    request.user.profile.save()
    return Response({"status": "success", "video": newVidPath})


@swagger_auto_schema(
    method="get",
    manual_parameters=[header_param],
)
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_new_video(request):
    user = request.user
    current_video_id = user.profile.last_viewed

    if not current_video_id or not current_video_id.isnumeric():
        new_video = Video.objects.order_by("?").first()
    else:
        new_video = Video.objects.exclude(pk=current_video_id).order_by("?").first()
    if not new_video:
        return Response({"video": None})
    user.profile.last_viewed = new_video.pk
    user.profile.save()
    serializer = VideoSerializer(new_video)
    return Response({"video":serializer.data})


@swagger_auto_schema(method="get", manual_parameters=[header_param])
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def videoplayer(request):
    video_pk = request.user.profile.last_viewed
    video = Video.objects.filter(pk=video_pk).first()
    if not video:
        video = Video.objects.order_by("?").first()
    if not video:
        return Response(status=404)
    video_path = video.file
    path = f"media/{video_path}"
    if not os.path.exists(path):
        return Response(status=404)
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
@authentication_classes([SessionAuthentication])
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
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(instance=category)
    return Response({"video": serializer.data})


# @swagger_auto_schema(
#     method="post",
#     manual_parameters=[header_param],
# )
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_comment(request):
    comment = CreateCommentSerializer(data=request.data)
    if comment.is_valid():
        comment.save()
        comment = CommentSerializer(instance=comment.instance)
        return Response({"comment": comment.data})
    return Response(comment.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    manual_parameters=[header_param],
)
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_videocomments(request, pk):
    comments = VideoComment.objects.filter(video_id=pk, linked_comment=None).order_by("-pk")
    serializer = CommentSerializer(comments, many=True)
    return Response({"comments": serializer.data})
    

class UserLogin(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    ##
    def post(self, request):
        data = request.data
        user = get_object_or_404(User, username=data.get("username"))
        if not user.check_password(data.get("password")):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(instance=user)
        user = serializer.check_user(data)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'user': serializer.data, 'token': token.key}, status=status.HTTP_200_OK)
    

class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    ##
    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({'user': serializer.data, 'token': token.key}, status=status.HTTP_200_OK)
    

class UserLogout(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CommentPoster(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        comment = CreateCommentSerializer(data=request.data)
        if comment.is_valid():
            comment.save()
            comment = CommentSerializer(instance=comment.instance)
            return Response({"comment": comment.data})
        return Response(comment.errors, status=status.HTTP_400_BAD_REQUEST)