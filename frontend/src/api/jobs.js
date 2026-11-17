import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

const SCALAR_FIELDS = ['title', 'address', 'city', 'state', 'start_date', 'end_date', 'description']

/**
 * Jobs are sent as multipart so the picture can travel with the rest of the form.
 * `image` is a File for a new upload; `removeImage` clears the stored one.
 */
function toFormData(job, { image, removeImage } = {}) {
  const form = new FormData()
  for (const field of SCALAR_FIELDS) {
    form.append(field, job[field] ?? '')
  }
  for (const status of job.statuses) form.append('statuses', status)
  for (const category of job.categories) form.append('categories', category)
  if (image) form.append('image', image)
  else if (removeImage) form.append('remove_image', 'true')
  return form
}

export async function listJobs({ search, status, signal } = {}) {
  const params = {}
  if (search) params.search = search
  if (status) params.status = status
  const { data } = await http.get('/jobs/', { params, signal })
  return data
}

export async function createJob(job, files) {
  const { data } = await http.post('/jobs/', toFormData(job, files))
  return data
}

export async function updateJob(id, job, files) {
  const { data } = await http.patch(`/jobs/${id}/`, toFormData(job, files))
  return data
}

export async function deleteJob(id) {
  await http.delete(`/jobs/${id}/`)
}

export async function duplicateJob(id) {
  const { data } = await http.post(`/jobs/${id}/duplicate/`)
  return data
}

export async function getJobOptions() {
  const { data } = await http.get('/jobs/options/')
  return data
}

export async function getAnalytics() {
  const { data } = await http.get('/jobs/analytics/')
  return data
}

/** Turns a DRF error response into `{ field: 'message' }` plus a general message. */
export function parseApiError(error) {
  const data = error?.response?.data
  if (!error?.response) {
    return { general: 'Could not reach the server. Is the Django API running?', fields: {} }
  }
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const fields = {}
    for (const [key, value] of Object.entries(data)) {
      fields[key] = Array.isArray(value) ? value.join(' ') : String(value)
    }
    const general = fields.non_field_errors || fields.detail || 'Please fix the highlighted fields.'
    return { general, fields }
  }
  return { general: `Request failed (${error.response.status}).`, fields: {} }
}
