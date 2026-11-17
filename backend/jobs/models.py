from django.contrib.postgres.fields import ArrayField
from django.db import models


class JobStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    REQUESTED = "requested", "Requested"
    POSTED = "posted", "Posted"
    FILLED = "filled", "Filled"


class JobCategory(models.TextChoices):
    FULL_TIME = "full_time", "Full-time"
    PART_TIME = "part_time", "Part-time"
    INTERN = "intern", "Intern"
    CONTRACT = "contract", "Contract"
    REMOTE = "remote", "Remote"


class Job(models.Model):
    image = models.ImageField(upload_to="jobs/%Y/%m/", blank=True)
    title = models.CharField(max_length=200)
    statuses = ArrayField(models.CharField(max_length=20, choices=JobStatus.choices))
    categories = ArrayField(models.CharField(max_length=20, choices=JobCategory.choices))
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    # Sanitized HTML from the rich text editor.
    description = models.TextField(blank=True)
    # Lower positions render first; lets a duplicate slot in directly below its source.
    position = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="job_end_date_not_before_start_date",
            ),
        ]

    def __str__(self):
        return self.title
