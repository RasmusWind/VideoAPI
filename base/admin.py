from django.contrib import admin
from .models import Video, Category, Profile, VideoComment
from nested_admin import NestedModelAdmin, NestedTabularInline
# Register your models here.


class LinkedCommentInline(NestedTabularInline):
    model = VideoComment
    extra = 0


class CommentInlineAdmin(NestedTabularInline):
    model = VideoComment
    inline = (LinkedCommentInline,)
    extra = 0


class CategoryInlineAdmin(admin.TabularInline):
    model = Video.categories.through
    extra = 1
    autocomplete_fields = ("category",)


class VideoInlineAdmin(admin.TabularInline):
    model = Category.videos.through
    extra = 1
    autocomplete_fields = ("video",)


@admin.register(Video)
class VideoAdmin(NestedModelAdmin):
    model = Video
    list_display = ("id", "name", "file")
    search_fields = ("name", "file")
    readonly_fields = (
        "link",
        "upload_date",
    )
    inlines = (CommentInlineAdmin,)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    search_fields = ("name",)
    inlines = (VideoInlineAdmin,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile

