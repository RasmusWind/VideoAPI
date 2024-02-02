from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from base.models import Video, Profile, Category


class CategoryVideosSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ("id", "name", "description", "file")


class VideoCategoriesSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class UserVideoSerializer(ModelSerializer):
    categories = VideoCategoriesSerializer(many=True)

    class Meta:
        model = Video
        fields = ("id", "name", "description", "file", "categories")
