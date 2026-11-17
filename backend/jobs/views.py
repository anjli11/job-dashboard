from django.core.files.base import ContentFile
from django.db import connection, transaction
from django.db.models import Count, F, Min
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Job, JobCategory, JobStatus
from .serializers import JobSerializer


def choices_payload(choices):
    return [{"value": value, "label": label} for value, label in choices.choices]


def lock_job_ordering():
    """Serialize writers that renumber positions. Must run inside a transaction."""
    with connection.cursor() as cursor:
        cursor.execute(f"LOCK TABLE {Job._meta.db_table} IN SHARE ROW EXCLUSIVE MODE")


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = Job.objects.all()
        params = self.request.query_params

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        status_filter = params.get("status", "").strip()
        if status_filter:
            if status_filter not in JobStatus.values:
                raise ValidationError({"status": f"Unknown status '{status_filter}'."})
            queryset = queryset.filter(statuses__contains=[status_filter])

        category_filter = params.get("category", "").strip()
        if category_filter:
            if category_filter not in JobCategory.values:
                raise ValidationError({"category": f"Unknown category '{category_filter}'."})
            queryset = queryset.filter(categories__contains=[category_filter])

        return queryset

    def perform_create(self, serializer):
        # New jobs go to the top of the grid.
        with transaction.atomic():
            lock_job_ordering()
            lowest = Job.objects.aggregate(lowest=Min("position"))["lowest"]
            serializer.save(position=(lowest - 1) if lowest is not None else 0)

    def perform_destroy(self, instance):
        image = instance.image if instance.image else None
        instance.delete()
        if image:
            image.storage.delete(image.name)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        source = self.get_object()
        with transaction.atomic():
            lock_job_ordering()
            Job.objects.filter(position__gt=source.position).update(position=F("position") + 1)

            copy = Job.objects.get(pk=source.pk)
            copy.pk = None
            copy.id = None
            copy.position = source.position + 1
            copy.image = ""
            copy.save()

            if source.image:
                # Give the copy its own file so deleting one job never breaks the other's picture.
                with source.image.open("rb") as fh:
                    copy.image.save(source.image.name.rsplit("/", 1)[-1], ContentFile(fh.read()), save=True)

        serializer = self.get_serializer(copy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def options(self, request):
        return Response(
            {
                "statuses": choices_payload(JobStatus),
                "categories": choices_payload(JobCategory),
            }
        )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        status_labels = dict(JobStatus.choices)
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT s, COUNT(*) FROM {Job._meta.db_table}, unnest(statuses) AS s
                GROUP BY s ORDER BY COUNT(*) DESC, s
                """
            )
            status_rows = cursor.fetchall()

        by_state = (
            Job.objects.values("state").annotate(count=Count("id")).order_by("-count", "state")
        )
        by_city = (
            Job.objects.values("city", "state").annotate(count=Count("id")).order_by("-count", "city")
        )

        return Response(
            {
                "total": Job.objects.count(),
                "by_status": [
                    {"status": value, "label": status_labels.get(value, value), "count": count}
                    for value, count in status_rows
                ],
                "by_state": list(by_state),
                "by_city": list(by_city),
            }
        )
