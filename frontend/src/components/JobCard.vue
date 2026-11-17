<script setup>
import { computed } from 'vue'
import { useTheme } from 'vuetify'
import { statusColor, useJobOptions } from '../composables/useJobOptions'
import { formatDateRange, stripHtml } from '../utils/format'

const props = defineProps({
  job: { type: Object, required: true },
  highlighted: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
})
const emit = defineEmits(['edit', 'duplicate', 'delete'])

const theme = useTheme()
const { statusLabel, categoryLabel } = useJobOptions()

const snippet = computed(() => stripHtml(props.job.description) || 'No description provided.')
const location = computed(() => [props.job.city, props.job.state].filter(Boolean).join(', '))
const initials = computed(() =>
  props.job.title
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join(''),
)
const isDark = computed(() => theme.global.current.value.dark)
</script>

<template>
  <v-card class="job-card" :class="{ 'job-card--highlight': highlighted }" border flat>
    <div class="job-card__media">
      <v-img v-if="job.image" :src="job.image" :alt="`${job.title} picture`" cover height="148">
        <template #placeholder>
          <div class="job-card__fallback"><v-progress-circular indeterminate size="24" color="white" /></div>
        </template>
      </v-img>
      <div v-else class="job-card__fallback" aria-hidden="true">
        <span>{{ initials }}</span>
      </div>

      <v-menu location="bottom end">
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            class="job-card__menu"
            icon="mdi-dots-horizontal"
            size="small"
            variant="flat"
            :loading="busy"
            :aria-label="`Actions for ${job.title}`"
          />
        </template>
        <v-list density="compact" min-width="170" nav>
          <v-list-item prepend-icon="mdi-pencil-outline" title="Edit" @click="emit('edit', job)" />
          <v-list-item prepend-icon="mdi-content-copy" title="Duplicate" @click="emit('duplicate', job)" />
          <v-divider class="my-1" />
          <v-list-item
            prepend-icon="mdi-trash-can-outline"
            title="Delete"
            base-color="error"
            @click="emit('delete', job)"
          />
        </v-list>
      </v-menu>
    </div>

    <div class="job-card__body">
      <h3 class="job-card__title" :title="job.title">{{ job.title }}</h3>

      <div class="job-card__statuses">
        <span v-for="s in job.statuses" :key="s" class="status-pill">
          <span class="status-dot" :style="{ background: statusColor(s, isDark) }" />
          {{ statusLabel[s] || s }}
        </span>
      </div>

      <p class="job-card__snippet">{{ snippet }}</p>

      <div class="job-card__meta">
        <div class="meta-row">
          <v-icon icon="mdi-map-marker-outline" size="16" />
          <span>{{ location }}</span>
        </div>
        <div class="meta-row">
          <v-icon icon="mdi-calendar-range" size="16" />
          <span>{{ formatDateRange(job.start_date, job.end_date) }}</span>
        </div>
      </div>

      <div class="job-card__categories">
        <v-chip v-for="c in job.categories" :key="c" size="small" variant="tonal" color="primary" label>
          {{ categoryLabel[c] || c }}
        </v-chip>
      </div>
    </div>
  </v-card>
</template>

<style scoped>
.job-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease,
    border-color 0.2s ease;
}
.job-card:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
.job-card--highlight {
  border-color: rgb(var(--v-theme-primary)) !important;
  animation: pulse 1.6s ease-out;
}
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--v-theme-primary), 0.45);
  }
  100% {
    box-shadow: 0 0 0 14px rgba(var(--v-theme-primary), 0);
  }
}
.job-card__media {
  position: relative;
  height: 148px;
  flex-shrink: 0;
}
.job-card__fallback {
  display: grid;
  place-items: center;
  height: 100%;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
  color: rgba(255, 255, 255, 0.92);
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.job-card__menu {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.92) !important;
  color: #0b0b0b !important;
  backdrop-filter: blur(4px);
}
.job-card__body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  flex: 1;
}
.job-card__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.01em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.job-card__statuses {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: rgba(var(--v-theme-on-surface), 0.86);
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.job-card__snippet {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: rgba(var(--v-theme-on-surface), 0.68);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: calc(1.5em * 3);
}
.job-card__meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-top: auto;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.job-card__categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
