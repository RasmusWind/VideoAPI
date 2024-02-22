from rest_framework.serializers import ModelSerializer, FileField, EmailField
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from base.models import Video, Profile, Category, VideoComment
from .related_serializers import (
    UserVideoSerializer,
    VideoCategoriesSerializer,
    CategoryVideosSerializer
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
    email = EmailField(required=False)
    
    def check_user(self, clean_data):
        user = authenticate(username=clean_data['username'], password=clean_data['password'])
        if not user:
            raise ValidationError('user not found')
        return user

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "videos", "profile")


class VideoSerializer(ModelSerializer):
    file = FileField()
    categories = VideoCategoriesSerializer(many=True, required=False)

    class Meta:
        model = Video
        fields = ("id", "name", "description", "file", "user", "categories")


class VideoCommentSerializer(ModelSerializer):
    created_date = serializers.DateTimeField(required=False)
    updated_date = serializers.DateTimeField(required=False)

    class Meta:
        model = VideoComment
        fields = ("id", "text", "video", "user", "linked_comment", "created_date", "updated_date")


class CreateCommentSerializer(ModelSerializer):
    class Meta:
        model = VideoComment
        fields = ("video", "text", "user")


class CommentUserSerializer(ModelSerializer):
    profile = ProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ("id", "username", "profile")

class LinkedCommentSerializer(ModelSerializer):
    user = CommentUserSerializer()
    created_date = serializers.DateTimeField(required=False)
    updated_date = serializers.DateTimeField(required=False)
    class Meta:
        model = VideoComment
        fields = ("id", "video", "user", "comments", "created_date", "updated_date", "text")

class CommentSerializer(ModelSerializer):
    user = CommentUserSerializer()
    comments = LinkedCommentSerializer(many=True, required=False)
    created_date = serializers.DateTimeField(required=False)
    updated_date = serializers.DateTimeField(required=False)

    class Meta:
        model = VideoComment
        fields = ("id", "video", "user", "comments", "created_date", "updated_date", "text")


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    ##
    def check_user(self, clean_data):
        user = authenticate(username=clean_data['username'], password=clean_data['password'])
        if not user:
            raise ValidationError('user not found')
        return user