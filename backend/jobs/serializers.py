import nh3
from django.conf import settings
from rest_framework import serializers

from .models import Job

ALLOWED_TAGS = {"p", "br", "strong", "b", "em", "i", "u", "s", "ul", "ol", "li", "h2", "h3", "blockquote", "code", "pre"}
ALLOWED_IMAGE_TYPES = {"JPEG", "PNG", "GIF", "WEBP"}


def unique_in_order(values):
    return list(dict.fromkeys(values))


class JobSerializer(serializers.ModelSerializer):
    # Write-only flag so an edit can clear the existing picture without uploading a new one.
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Job
        fields = [
            "id",
            "image",
            "remove_image",
            "title",
            "statuses",
            "categories",
            "address",
            "city",
            "state",
            "start_date",
            "end_date",
            "description",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "position", "created_at", "updated_at"]
        extra_kwargs = {
            "statuses": {"allow_empty": False},
            "categories": {"allow_empty": False},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Relative URL so media resolves through whatever host/proxy served the API.
        data["image"] = instance.image.url if instance.image else None
        return data

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Job title is required.")
        return value

    def validate_city(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("City is required.")
        return value

    def validate_state(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("State is required.")
        return value

    def validate_address(self, value):
        return value.strip()

    def validate_statuses(self, value):
        return unique_in_order(value)

    def validate_categories(self, value):
        return unique_in_order(value)

    def validate_description(self, value):
        return nh3.clean(value, tags=ALLOWED_TAGS, attributes={}).strip()

    def validate_image(self, value):
        if not value:
            return value
        if value.size > settings.JOB_IMAGE_MAX_BYTES:
            limit_mb = settings.JOB_IMAGE_MAX_BYTES // (1024 * 1024)
            raise serializers.ValidationError(f"Image must be {limit_mb} MB or smaller.")
        # DRF's ImageField has already opened the file with Pillow and attached the result.
        image_format = getattr(getattr(value, "image", None), "format", None)
        if image_format not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Upload a JPEG, PNG, GIF or WebP image.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "End date cannot be before the start date."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("remove_image", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove_image = validated_data.pop("remove_image", False)
        new_image = validated_data.get("image")
        old_image = instance.image if instance.image else None
        if remove_image and not new_image:
            validated_data["image"] = ""
        instance = super().update(instance, validated_data)
        if old_image and (new_image or remove_image) and old_image.name != instance.image.name:
            old_image.storage.delete(old_image.name)
        return instance
