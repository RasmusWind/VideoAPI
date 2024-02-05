from rest_framework.serializers import ModelSerializer, FileField
from django.contrib.auth.models import User
from base.models import Video, Profile, Category
from .related_serializers import (
    UserVideoSerializer,
    VideoCategoriesSerializer,
    CategoryVideosSerializer,
)


class CategorySerializer(ModelSerializer):
    videos = CategoryVideosSerializer(many=True)

    class Meta:
        model = Category
        fields = ("id", "name", "videos")


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ("image", "last_viewed")


class UserSerializer(ModelSerializer):
    videos = UserVideoSerializer(many=True, required=False)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ("id", "username", "password", "videos", "profile")


class VideoSerializer(ModelSerializer):
    file = FileField()
    categories = VideoCategoriesSerializer(many=True)

    class Meta:
        model = Video
        fields = ("id", "name", "description", "file", "user", "categories")
