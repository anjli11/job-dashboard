import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase

from .models import Job

MEDIA_ROOT = tempfile.mkdtemp()


def png_upload(name="pic.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), (200, 50, 50)).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def payload(**overrides):
    data = {
        "title": "Backend Engineer",
        "statuses": ["posted"],
        "categories": ["full_time"],
        "address": "1 Main St",
        "city": "Austin",
        "state": "TX",
        "start_date": "2026-01-01",
        "end_date": "2026-03-01",
        "description": "<p>Hello</p>",
    }
    data.update(overrides)
    return data


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JobApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def create(self, **overrides):
        response = self.client.post("/api/jobs/", payload(**overrides), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_create_and_list(self):
        self.create()
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Backend Engineer")

    def test_new_jobs_appear_first(self):
        self.create(title="First")
        self.create(title="Second")
        titles = [job["title"] for job in self.client.get("/api/jobs/").data]
        self.assertEqual(titles, ["Second", "First"])

    def test_end_date_before_start_date_rejected(self):
        response = self.client.post(
            "/api/jobs/", payload(start_date="2026-05-01", end_date="2026-04-01"), format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("end_date", response.data)

    def test_partial_update_checks_dates_against_stored_values(self):
        job = self.create()
        response = self.client.patch(f"/api/jobs/{job['id']}/", {"end_date": "2025-12-01"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("end_date", response.data)

    def test_required_fields_and_choices(self):
        response = self.client.post(
            "/api/jobs/",
            payload(title="   ", statuses=[], categories=["bogus"], city=""),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        for field in ("title", "statuses", "categories", "city"):
            self.assertIn(field, response.data)

    def test_description_is_sanitized(self):
        job = self.create(description='<p onclick="x()">Hi</p><script>alert(1)</script>')
        self.assertEqual(job["description"], "<p>Hi</p>")

    def test_search_and_status_filter(self):
        self.create(title="Python Developer", statuses=["posted"])
        self.create(title="Designer", statuses=["draft"])
        self.create(title="Senior Python Lead", statuses=["draft", "requested"])

        titles = {j["title"] for j in self.client.get("/api/jobs/", {"search": "python"}).data}
        self.assertEqual(titles, {"Python Developer", "Senior Python Lead"})

        titles = {j["title"] for j in self.client.get("/api/jobs/", {"status": "draft"}).data}
        self.assertEqual(titles, {"Designer", "Senior Python Lead"})

        titles = {j["title"] for j in self.client.get("/api/jobs/", {"search": "python", "status": "draft"}).data}
        self.assertEqual(titles, {"Senior Python Lead"})

        self.assertEqual(self.client.get("/api/jobs/", {"status": "nope"}).status_code, 400)

    def test_duplicate_inserts_directly_below_original(self):
        bottom = self.create(title="Bottom")
        middle = self.create(title="Middle")
        self.create(title="Top")

        response = self.client.post(f"/api/jobs/{middle['id']}/duplicate/")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], middle["id"])

        jobs = self.client.get("/api/jobs/").data
        self.assertEqual([j["title"] for j in jobs], ["Top", "Middle", "Middle", "Bottom"])
        self.assertEqual(jobs[1]["id"], middle["id"])
        self.assertEqual(jobs[2]["id"], response.data["id"])
        self.assertEqual(jobs[3]["id"], bottom["id"])

        for field in ("statuses", "categories", "city", "state", "start_date", "end_date", "description"):
            self.assertEqual(jobs[2][field], middle[field])

    def test_image_upload_duplicate_and_delete(self):
        data = payload(image=png_upload())
        response = self.client.post("/api/jobs/", data, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        job = Job.objects.get(pk=response.data["id"])
        self.assertTrue(job.image)

        copy_id = self.client.post(f"/api/jobs/{job.id}/duplicate/").data["id"]
        copy = Job.objects.get(pk=copy_id)
        self.assertTrue(copy.image)
        self.assertNotEqual(copy.image.name, job.image.name)

        self.assertEqual(self.client.delete(f"/api/jobs/{job.id}/").status_code, 204)
        self.assertFalse(job.image.storage.exists(job.image.name))
        self.assertTrue(copy.image.storage.exists(copy.image.name))

    def test_remove_image_on_update(self):
        response = self.client.post("/api/jobs/", payload(image=png_upload()), format="multipart")
        job = Job.objects.get(pk=response.data["id"])
        old_name = job.image.name

        response = self.client.patch(f"/api/jobs/{job.id}/", {"remove_image": True}, format="multipart")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNone(response.data["image"])
        self.assertFalse(job.image.storage.exists(old_name))

    def test_rejects_non_image_upload(self):
        bad = SimpleUploadedFile("evil.png", b"not an image", content_type="image/png")
        response = self.client.post("/api/jobs/", payload(image=bad), format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("image", response.data)

    def test_delete(self):
        job = self.create()
        self.assertEqual(self.client.delete(f"/api/jobs/{job['id']}/").status_code, 204)
        self.assertFalse(Job.objects.exists())

    def test_analytics(self):
        self.create(statuses=["posted"], city="Austin", state="TX")
        self.create(statuses=["posted", "draft"], city="Dallas", state="TX")
        self.create(statuses=["filled"], city="Austin", state="TX")
        self.create(statuses=["draft"], city="Seattle", state="WA")

        data = self.client.get("/api/jobs/analytics/").data
        self.assertEqual(data["total"], 4)
        self.assertEqual({s["status"]: s["count"] for s in data["by_status"]}, {"posted": 2, "draft": 2, "filled": 1})
        self.assertEqual({s["state"]: s["count"] for s in data["by_state"]}, {"TX": 3, "WA": 1})
        self.assertEqual(data["by_city"][0], {"city": "Austin", "state": "TX", "count": 2})

    def test_options(self):
        data = self.client.get("/api/jobs/options/").data
        self.assertIn({"value": "draft", "label": "Draft"}, data["statuses"])
        self.assertIn({"value": "intern", "label": "Intern"}, data["categories"])
