from django.contrib import admin
from .models import Video, Category, Profile
# Register your models here.


class CategoryInlineAdmin(admin.TabularInline):
    model = Video.categories.through
    extra = 1
    autocomplete_fields = ("category",)


class VideoInlineAdmin(admin.TabularInline):
    model = Category.videos.through
    extra = 1
    autocomplete_fields = ("video",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    model = Video
    search_fields = ("name", "file")
    readonly_fields = (
        "link",
        "upload_date",
    )
    inlines = (CategoryInlineAdmin,)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    search_fields = ("name",)
    inlines = (VideoInlineAdmin,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile
