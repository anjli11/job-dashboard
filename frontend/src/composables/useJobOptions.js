import { computed, ref } from 'vue'
import { getJobOptions } from '../api/jobs'

// Fallback mirrors the backend choices so the UI still renders if /options/ is slow.
const options = ref({
  statuses: [
    { value: 'draft', label: 'Draft' },
    { value: 'requested', label: 'Requested' },
    { value: 'posted', label: 'Posted' },
    { value: 'filled', label: 'Filled' },
  ],
  categories: [
    { value: 'full_time', label: 'Full-time' },
    { value: 'part_time', label: 'Part-time' },
    { value: 'intern', label: 'Intern' },
    { value: 'contract', label: 'Contract' },
    { value: 'remote', label: 'Remote' },
  ],
})
let request = null

/**
 * Status colors are assigned by entity (fixed order), never by rank, so a status keeps
 * the same color on cards, filters and charts. Slots come from the validated
 * categorical palette, stepped separately for light and dark surfaces.
 */
const STATUS_COLORS = {
  draft: { light: '#2a78d6', dark: '#3987e5' },
  requested: { light: '#eb6834', dark: '#d95926' },
  posted: { light: '#1baf7a', dark: '#199e70' },
  filled: { light: '#eda100', dark: '#c98500' },
}

export function statusColor(value, dark = false) {
  const entry = STATUS_COLORS[value]
  if (!entry) return '#898781'
  return dark ? entry.dark : entry.light
}

export function useJobOptions() {
  if (!request) {
    request = getJobOptions()
      .then((data) => {
        options.value = data
      })
      .catch(() => {
        request = null
      })
  }

  const statusLabel = computed(() => Object.fromEntries(options.value.statuses.map((o) => [o.value, o.label])))
  const categoryLabel = computed(() => Object.fromEntries(options.value.categories.map((o) => [o.value, o.label])))

  return {
    statusOptions: computed(() => options.value.statuses),
    categoryOptions: computed(() => options.value.categories),
    statusLabel,
    categoryLabel,
  }
}
