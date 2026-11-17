<script setup>
import axios from 'axios'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { deleteJob, duplicateJob, listJobs, parseApiError } from '../api/jobs'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import JobCard from '../components/JobCard.vue'
import JobFormDialog from '../components/JobFormDialog.vue'
import { statusColor, useJobOptions } from '../composables/useJobOptions'

const route = useRoute()
const router = useRouter()
const theme = useTheme()
const { statusOptions } = useJobOptions()

const jobs = ref([])
const loading = ref(true)
const loadError = ref('')
const hasLoadedOnce = ref(false)

const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const statusFilter = ref(typeof route.query.status === 'string' ? route.query.status : null)
const debouncedSearch = ref(search.value)

const formOpen = ref(false)
const editingJob = ref(null)
const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const busyId = ref(null)
const highlightId = ref(null)
const snackbar = ref({ show: false, text: '', color: 'success' })

const filtersActive = computed(() => Boolean(debouncedSearch.value.trim() || statusFilter.value))
const isDark = computed(() => theme.global.current.value.dark)

let controller = null
let searchTimer = null
let highlightTimer = null

async function fetchJobs({ silent = false } = {}) {
  controller?.abort()
  const current = new AbortController()
  controller = current
  if (!silent) loading.value = true
  loadError.value = ''
  try {
    jobs.value = await listJobs({
      search: debouncedSearch.value.trim(),
      status: statusFilter.value,
      signal: current.signal,
    })
    hasLoadedOnce.value = true
  } catch (error) {
    if (axios.isCancel(error)) return
    loadError.value = parseApiError(error).general
  } finally {
    // A superseded request leaves the spinner to the one that replaced it.
    if (!current.signal.aborted) loading.value = false
  }
}

watch(search, (value) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    debouncedSearch.value = value
  }, 300)
})

watch([debouncedSearch, statusFilter], ([q, status]) => {
  const query = { ...route.query, q: q.trim() || undefined, status: status || undefined }
  router.replace({ query })
  fetchJobs()
})

onMounted(fetchJobs)
onBeforeUnmount(() => {
  controller?.abort()
  clearTimeout(searchTimer)
  clearTimeout(highlightTimer)
})

function notify(text, color = 'success') {
  snackbar.value = { show: true, text, color }
}

function highlight(id) {
  highlightId.value = id
  clearTimeout(highlightTimer)
  highlightTimer = setTimeout(() => {
    highlightId.value = null
  }, 1800)
  nextTick(() => {
    document.getElementById(`job-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  })
}

function clearFilters() {
  search.value = ''
  debouncedSearch.value = ''
  statusFilter.value = null
}

function openCreate() {
  editingJob.value = null
  formOpen.value = true
}

function openEdit(job) {
  editingJob.value = job
  formOpen.value = true
}

function onSaved(saved, { created }) {
  if (created) {
    jobs.value.unshift(saved)
    notify('Job posted.')
  } else {
    const index = jobs.value.findIndex((j) => j.id === saved.id)
    if (index !== -1) jobs.value.splice(index, 1, saved)
    notify('Changes saved.')
  }
  highlight(saved.id)
  // Re-sync quietly so active filters still apply to the new/edited job.
  if (filtersActive.value) fetchJobs({ silent: true })
}

async function onDuplicate(job) {
  busyId.value = job.id
  try {
    const copy = await duplicateJob(job.id)
    const index = jobs.value.findIndex((j) => j.id === job.id)
    jobs.value.splice(index + 1, 0, copy)
    highlight(copy.id)
    notify('Job duplicated.')
  } catch (error) {
    notify(parseApiError(error).general, 'error')
  } finally {
    busyId.value = null
  }
}

function askDelete(job) {
  pendingDelete.value = job
  confirmOpen.value = true
}

async function confirmDelete() {
  const job = pendingDelete.value
  if (!job) return
  deleting.value = true
  try {
    await deleteJob(job.id)
    jobs.value = jobs.value.filter((j) => j.id !== job.id)
    confirmOpen.value = false
    notify('Job deleted.')
  } catch (error) {
    notify(parseApiError(error).general, 'error')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Job postings</h1>
        <p class="page-subtitle">
          <template v-if="hasLoadedOnce">
            {{ jobs.length }} {{ jobs.length === 1 ? 'job' : 'jobs' }}{{ filtersActive ? ' match your filters' : ' in total' }}
          </template>
          <template v-else>Create, manage and track your open roles.</template>
        </p>
      </div>
      <v-btn color="primary" size="large" variant="flat" prepend-icon="mdi-plus" @click="openCreate">Post job</v-btn>
    </header>

    <div class="toolbar panel">
      <v-text-field
        v-model="search"
        class="toolbar__search"
        placeholder="Search jobs by title…"
        prepend-inner-icon="mdi-magnify"
        density="compact"
        variant="solo-filled"
        flat
        clearable
        hide-details
        aria-label="Search jobs by title"
        @click:clear="debouncedSearch = ''"
      />
      <v-select
        v-model="statusFilter"
        class="toolbar__status"
        :items="statusOptions"
        item-title="label"
        item-value="value"
        placeholder="All statuses"
        prepend-inner-icon="mdi-filter-variant"
        density="compact"
        variant="solo-filled"
        flat
        clearable
        hide-details
        aria-label="Filter by status"
      >
        <template #item="{ props: itemProps, item }">
          <v-list-item v-bind="itemProps">
            <template #prepend>
              <span class="dot" :style="{ background: statusColor(item.value, isDark) }" />
            </template>
          </v-list-item>
        </template>
      </v-select>
    </div>

    <div v-if="loading" class="state-center" role="status" aria-live="polite">
      <v-progress-circular indeterminate color="primary" size="48" width="4" />
      <span class="text-muted mt-4">Loading jobs…</span>
    </div>

    <EmptyState
      v-else-if="loadError"
      icon="mdi-cloud-alert-outline"
      title="Couldn't load jobs"
      :message="loadError"
    >
      <v-btn color="primary" variant="flat" prepend-icon="mdi-refresh" @click="fetchJobs()">Try again</v-btn>
    </EmptyState>

    <EmptyState
      v-else-if="jobs.length === 0 && filtersActive"
      icon="mdi-text-search"
      title="No jobs found"
      message="No postings match your search or status filter. Try a different keyword or clear the filters."
    >
      <v-btn variant="tonal" prepend-icon="mdi-filter-remove-outline" @click="clearFilters">Clear filters</v-btn>
    </EmptyState>

    <EmptyState
      v-else-if="jobs.length === 0"
      icon="mdi-briefcase-plus-outline"
      title="No jobs found"
      message="You haven't posted any jobs yet. Create your first posting to see it here."
    >
      <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" @click="openCreate">Post your first job</v-btn>
    </EmptyState>

    <transition-group v-else name="grid" tag="div" class="job-grid">
      <div v-for="job in jobs" :id="`job-${job.id}`" :key="job.id" class="job-grid__item">
        <JobCard
          :job="job"
          :highlighted="highlightId === job.id"
          :busy="busyId === job.id"
          @edit="openEdit"
          @duplicate="onDuplicate"
          @delete="askDelete"
        />
      </div>
    </transition-group>

    <JobFormDialog v-model="formOpen" :job="editingJob" @saved="onSaved" />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Delete this job?"
      :message="pendingDelete ? `“${pendingDelete.title}” will be permanently removed. This can't be undone.` : ''"
      confirm-text="Delete"
      :loading="deleting"
      @confirm="confirmDelete"
    />

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="2600" location="bottom right">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px;
  margin-bottom: 24px;
}
.toolbar__search {
  flex: 1 1 280px;
}
.toolbar__status {
  flex: 0 1 220px;
  min-width: 180px;
}
@media (max-width: 600px) {
  .toolbar__status {
    flex: 1 1 100%;
  }
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 12px;
}
.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 96px 0;
}
.job-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.job-grid__item {
  min-width: 0;
}
.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
.grid-enter-active,
.grid-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.grid-move {
  transition: transform 0.3s ease;
}
</style>
