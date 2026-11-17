# JobBoard — Job Postings Dashboard

A responsive web app to create, manage and analyze job postings.

- **Frontend:** Vue 3 + Vite, Vuetify 4, vue-router, Chart.js (vue-chartjs), TipTap rich text editor
- **Backend:** Django 5.2 + Django REST Framework
- **Database:** PostgreSQL (array columns for multi-select status/category)

## Features

| Area | What's included |
|---|---|
| Dashboard | Responsive card grid: header picture (or gradient initials fallback), title, description snippet, status, categories, city/state, date range |
| Card actions | Edit (pre-filled dialog), Delete (confirmation dialog), Duplicate (copy — including its own copy of the image — inserted directly below the original) |
| Create / edit form | Drag-and-drop image zone with preview, title, multi-select status & category, address/city/state, start/end date, rich text description |
| Analytics | Stat tiles, status distribution donut (pie) chart, jobs by state and by city bar charts; every chart has a table view |
| Validation | Frontend rules + backend serializer validation + a DB check constraint (`end_date >= start_date`); image type/size checks; HTML description sanitized server-side with `nh3` |
| Search & filter | Debounced title search and status filter (server-side, synced to the URL) |
| States | Loading spinners, error state with retry, "No jobs found" empty states (empty DB vs. no filter matches) |
| Extras | Light/dark theme toggle, toast notifications, keyboard-accessible dropzone and editor toolbar |

## Running locally

Prerequisites: Python 3.10+, Node 20+, PostgreSQL running locally.

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env            # adjust POSTGRES_* if needed
createdb job_postings
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jobs      # optional: 12 sample jobs with images (--clear to reset)
.venv/bin/python manage.py runserver 8000
```

Run the tests with `.venv/bin/python manage.py test jobs`.

### Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173 (use `-- --port 5174` if 5173 is taken)
```

The Vite dev server proxies `/api` and `/media` to `http://127.0.0.1:8000`
(override with `VITE_PROXY_TARGET`). For a separately hosted API, build with `VITE_API_URL=https://api.example.com/api`.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/jobs/?search=&status=&category=` | List jobs (ordered by position) |
| POST | `/api/jobs/` | Create (multipart; `statuses`/`categories` as repeated keys, optional `image`) |
| GET / PATCH / PUT / DELETE | `/api/jobs/{id}/` | Retrieve / update (`remove_image=true` clears the picture) / delete |
| POST | `/api/jobs/{id}/duplicate/` | Duplicate a job directly below the original |
| GET | `/api/jobs/options/` | Status and category choices |
| GET | `/api/jobs/analytics/` | Totals, counts by status, state and city |

## Notes

- Ordering uses a `position` column: new jobs go to the top; a duplicate shifts later rows down by one and
  takes `original.position + 1`. Writers that renumber take a table lock so concurrent duplicates can't collide.
- Status is multi-select per the spec, so the status chart counts status *tags*; the table view also shows the
  percentage of jobs carrying each status.
- There is no authentication — the API is open (`AllowAny`). Add auth before deploying anywhere public.
