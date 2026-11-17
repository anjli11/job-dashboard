import io
import random
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from jobs.models import Job

SAMPLE_JOBS = [
    ("Senior Backend Engineer", ["posted"], ["full_time"], "Austin", "TX"),
    ("Frontend Developer (Vue)", ["posted"], ["full_time", "remote"], "San Francisco", "CA"),
    ("Data Analyst Intern", ["requested"], ["intern"], "New York", "NY"),
    ("Product Designer", ["draft"], ["full_time"], "Seattle", "WA"),
    ("DevOps Engineer", ["posted", "requested"], ["contract"], "Austin", "TX"),
    ("Customer Success Associate", ["filled"], ["part_time"], "Chicago", "IL"),
    ("Machine Learning Engineer", ["posted"], ["full_time"], "San Francisco", "CA"),
    ("QA Automation Engineer", ["draft"], ["contract", "remote"], "Denver", "CO"),
    ("Marketing Coordinator", ["filled"], ["full_time"], "New York", "NY"),
    ("Technical Writer", ["requested"], ["part_time", "remote"], "Portland", "OR"),
    ("Mobile Engineer (iOS)", ["posted"], ["full_time"], "Los Angeles", "CA"),
    ("Sales Development Intern", ["draft", "requested"], ["intern"], "Dallas", "TX"),
]

PALETTE = [
    ((79, 70, 229), (124, 58, 237)),
    ((14, 165, 233), (16, 185, 129)),
    ((236, 72, 153), (249, 115, 22)),
    ((30, 64, 175), (56, 189, 248)),
    ((5, 150, 105), (132, 204, 22)),
    ((190, 18, 60), (234, 88, 12)),
]

DESCRIPTION = (
    "<p>We're looking for a <strong>{title}</strong> to join our growing team in {city}.</p>"
    "<ul><li>Collaborate with a cross-functional team</li>"
    "<li>Ship meaningful work from day one</li>"
    "<li>Competitive pay and flexible hours</li></ul>"
)


def gradient_png(start, end, size=(800, 400)):
    width, height = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for x in range(width):
        t = x / (width - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(start, end))
        draw.line([(x, 0), (x, height)], fill=color)
    # A few soft circles so the headers aren't flat.
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    rng = random.Random(sum(start) + sum(end))
    for _ in range(5):
        r = rng.randint(60, 180)
        cx, cy = rng.randint(0, width), rng.randint(0, height)
        odraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 28))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "Populate the database with sample job postings."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete existing jobs first.")

    def handle(self, *args, clear=False, **options):
        if clear:
            for job in Job.objects.exclude(image=""):
                job.image.delete(save=False)
            Job.objects.all().delete()

        start_position = (Job.objects.order_by("position").values_list("position", flat=True).first() or 0) - len(
            SAMPLE_JOBS
        )
        today = date.today()
        for index, (title, statuses, categories, city, state) in enumerate(SAMPLE_JOBS):
            start = today + timedelta(days=7 * index)
            job = Job(
                title=title,
                statuses=statuses,
                categories=categories,
                address=f"{100 + index * 7} Main Street",
                city=city,
                state=state,
                start_date=start,
                end_date=start + timedelta(days=90 + 30 * (index % 4)),
                description=DESCRIPTION.format(title=title, city=city),
                position=start_position + index,
            )
            colors = PALETTE[index % len(PALETTE)]
            job.image.save(f"seed-{index + 1}.png", ContentFile(gradient_png(*colors)), save=False)
            job.save()

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_JOBS)} sample jobs."))
