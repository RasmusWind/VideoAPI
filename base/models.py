import magic
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from .video_extensions import video_extensions
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

file_extension_validator = FileExtensionValidator(video_extensions)


def validate_file_mimetype(file):
    accept = [f"video/{ext}" for ext in video_extensions]
    accept.append("application/octet-stream")
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(f"Unsupported file type: {file_mime_type}")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_viewed = models.CharField(max_length=200, null=True)
    image = models.ImageField(
        default="default_profile_picture.png", upload_to="profile_pics"
    )

    def __str__(self):
        end = "'"  # Cannot have backslashes in f-string expressions.
        return f"{self.user.username + end + ('s' if not self.user.username[-1] == 's' else '')} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Video(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="video_uploads/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[file_extension_validator, validate_file_mimetype],
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        related_name="videos",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    categories = models.ManyToManyField("base.Category", through="base.VideoCategory")

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)

    @property
    def link(self):
        if self.file:
            return f"http://127.0.0.1:8000{self.file.url}"
        return "No file"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    videos = models.ManyToManyField("base.Video", through="base.VideoCategory")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class VideoCategory(models.Model):
    video = models.ForeignKey(
        "base.Video", related_name="video_categories", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "base.Category", related_name="category_videos", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Video Categories"


class VideoComment(models.Model):
    video = models.ForeignKey("base.Video", related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    linked_comment = models.ForeignKey("base.VideoComment", related_name="comments", null=True, blank=True, on_delete=models.SET_NULL)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    text = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"Comment by: {self.user} on: {self.linked_comment if self.linked_comment else self.video}"