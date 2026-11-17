<script setup>
import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, LinearScale, Tooltip } from 'chart.js'
import { computed, onMounted, ref } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { useTheme } from 'vuetify'
import { getAnalytics, parseApiError } from '../api/jobs'
import ChartPanel from '../components/ChartPanel.vue'
import EmptyState from '../components/EmptyState.vue'
import { statusColor } from '../composables/useJobOptions'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip)

const MAX_BARS = 10

const theme = useTheme()
const isDark = computed(() => theme.global.current.value.dark)

const data = ref(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = await getAnalytics()
  } catch (err) {
    error.value = parseApiError(err).general
  } finally {
    loading.value = false
  }
}
onMounted(load)

// Chart chrome per mode (hairline grid, recessive axes, ink for text).
const ink = computed(() =>
  isDark.value
    ? { surface: '#1a1a19', primary: '#f0efec', secondary: '#c3c2b7', muted: '#898781', grid: '#2c2c2a', series: '#3987e5' }
    : { surface: '#ffffff', primary: '#0b0b0b', secondary: '#52514e', muted: '#898781', grid: '#e1e0d9', series: '#2a78d6' },
)

const total = computed(() => data.value?.total ?? 0)
const statusTagTotal = computed(() => (data.value?.by_status ?? []).reduce((sum, s) => sum + s.count, 0))
const pct = (n, d) => (d ? `${Math.round((n / d) * 1000) / 10}%` : '0%')

const stats = computed(() => {
  const d = data.value
  if (!d) return []
  const posted = d.by_status.find((s) => s.status === 'posted')?.count ?? 0
  const filled = d.by_status.find((s) => s.status === 'filled')?.count ?? 0
  return [
    { label: 'Total jobs', value: d.total, icon: 'mdi-briefcase-outline' },
    { label: 'Posted', value: posted, icon: 'mdi-bullhorn-outline' },
    { label: 'Filled', value: filled, icon: 'mdi-check-decagram-outline' },
    { label: 'Cities', value: d.by_city.length, icon: 'mdi-city-variant-outline' },
    { label: 'States', value: d.by_state.length, icon: 'mdi-map-outline' },
  ]
})

const statusRows = computed(() =>
  (data.value?.by_status ?? []).map((s) => ({
    ...s,
    color: statusColor(s.status, isDark.value),
    share: pct(s.count, statusTagTotal.value),
    ofJobs: pct(s.count, total.value),
  })),
)

const statusChartData = computed(() => ({
  labels: statusRows.value.map((s) => s.label),
  datasets: [
    {
      data: statusRows.value.map((s) => s.count),
      backgroundColor: statusRows.value.map((s) => s.color),
      // A surface-colored ring gives a 2px gap between slices.
      borderColor: ink.value.surface,
      borderWidth: 2,
      hoverOffset: 6,
    },
  ],
}))

function tooltipStyle() {
  return {
    backgroundColor: isDark.value ? '#2c2c2a' : '#0b0b0b',
    titleColor: '#f0efec',
    bodyColor: '#f0efec',
    padding: 10,
    cornerRadius: 8,
    displayColors: true,
    boxPadding: 4,
    titleFont: { family: 'Inter', weight: '600' },
    bodyFont: { family: 'Inter' },
  }
}

const statusChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '62%',
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipStyle(),
      callbacks: {
        label: (ctx) => {
          const row = statusRows.value[ctx.dataIndex]
          return ` ${row.count} ${row.count === 1 ? 'job' : 'jobs'} · ${row.share} of status tags`
        },
      },
    },
  },
}))

// Long tails fold into "Other" so the bar list stays readable.
function foldRows(rows, labelOf) {
  const sorted = [...rows].sort((a, b) => b.count - a.count)
  if (sorted.length <= MAX_BARS) return sorted.map((r) => ({ label: labelOf(r), count: r.count }))
  const head = sorted.slice(0, MAX_BARS - 1).map((r) => ({ label: labelOf(r), count: r.count }))
  const rest = sorted.slice(MAX_BARS - 1)
  head.push({ label: `Other (${rest.length})`, count: rest.reduce((s, r) => s + r.count, 0) })
  return head
}

const stateRows = computed(() => foldRows(data.value?.by_state ?? [], (r) => r.state))
const cityRows = computed(() => foldRows(data.value?.by_city ?? [], (r) => `${r.city}, ${r.state}`))

function barData(rows) {
  return {
    labels: rows.map((r) => r.label),
    datasets: [
      {
        data: rows.map((r) => r.count),
        backgroundColor: ink.value.series,
        hoverBackgroundColor: isDark.value ? '#5598e7' : '#1c5cab',
        borderRadius: 4,
        borderSkipped: 'start',
        maxBarThickness: 18,
        categoryPercentage: 0.8,
        barPercentage: 0.9,
      },
    ],
  }
}

const barOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipStyle(),
      displayColors: false,
      callbacks: {
        label: (ctx) => ` ${ctx.parsed.x} ${ctx.parsed.x === 1 ? 'job' : 'jobs'} · ${pct(ctx.parsed.x, total.value)} of all jobs`,
      },
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: { precision: 0, color: ink.value.muted, font: { family: 'Inter', size: 11 } },
      grid: { color: ink.value.grid, drawTicks: false },
      border: { display: false },
    },
    y: {
      ticks: { color: ink.value.secondary, font: { family: 'Inter', size: 12 } },
      grid: { display: false },
      border: { color: ink.value.grid },
    },
  },
}))

const barHeight = (rows) => `${Math.max(160, rows.length * 34 + 40)}px`
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Analytics</h1>
        <p class="page-subtitle">A snapshot of every job currently in the database.</p>
      </div>
      <v-btn variant="tonal" prepend-icon="mdi-refresh" :loading="loading" @click="load">Refresh</v-btn>
    </header>

    <div v-if="loading && !data" class="state-center" role="status" aria-live="polite">
      <v-progress-circular indeterminate color="primary" size="48" width="4" />
      <span class="text-muted mt-4">Crunching numbers…</span>
    </div>

    <EmptyState v-else-if="error" icon="mdi-cloud-alert-outline" title="Couldn't load analytics" :message="error">
      <v-btn color="primary" variant="flat" prepend-icon="mdi-refresh" @click="load">Try again</v-btn>
    </EmptyState>

    <EmptyState
      v-else-if="total === 0"
      icon="mdi-chart-donut"
      title="No jobs found"
      message="There's nothing to analyze yet. Post a job and the charts will appear here."
    >
      <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" :to="{ name: 'jobs' }">Go to jobs</v-btn>
    </EmptyState>

    <template v-else>
      <div class="stats">
        <div v-for="stat in stats" :key="stat.label" class="stat panel">
          <div class="stat__icon"><v-icon :icon="stat.icon" size="20" /></div>
          <div>
            <div class="stat__value">{{ stat.value }}</div>
            <div class="stat__label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <div class="charts">
        <ChartPanel
          class="charts__status"
          title="Status distribution"
          subtitle="Share of status tags across all jobs. A job can carry more than one status."
        >
          <template #chart>
            <div class="donut-layout">
              <div class="donut">
                <Doughnut :data="statusChartData" :options="statusChartOptions" aria-label="Status distribution pie chart" role="img" />
                <div class="donut__center" aria-hidden="true">
                  <div class="donut__value">{{ total }}</div>
                  <div class="donut__label">jobs</div>
                </div>
              </div>
              <ul class="legend" aria-label="Status legend">
                <li v-for="row in statusRows" :key="row.status" class="legend__item">
                  <span class="legend__swatch" :style="{ background: row.color }" />
                  <span class="legend__name">{{ row.label }}</span>
                  <span class="legend__value">{{ row.share }}</span>
                  <span class="legend__count">{{ row.count }}</span>
                </li>
              </ul>
            </div>
          </template>
          <template #table>
            <v-table density="compact">
              <thead>
                <tr>
                  <th>Status</th>
                  <th class="text-right">Jobs</th>
                  <th class="text-right">Share of tags</th>
                  <th class="text-right">% of jobs</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in statusRows" :key="row.status">
                  <td><span class="legend__swatch mr-2" :style="{ background: row.color }" />{{ row.label }}</td>
                  <td class="text-right num">{{ row.count }}</td>
                  <td class="text-right num">{{ row.share }}</td>
                  <td class="text-right num">{{ row.ofJobs }}</td>
                </tr>
              </tbody>
            </v-table>
          </template>
        </ChartPanel>

        <ChartPanel title="Jobs by state" :subtitle="`${data.by_state.length} ${data.by_state.length === 1 ? 'state' : 'states'}`">
          <template #chart>
            <div :style="{ height: barHeight(stateRows) }">
              <Bar :data="barData(stateRows)" :options="barOptions" aria-label="Jobs by state bar chart" role="img" />
            </div>
          </template>
          <template #table>
            <v-table density="compact">
              <thead>
                <tr><th>State</th><th class="text-right">Jobs</th><th class="text-right">% of jobs</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in data.by_state" :key="row.state">
                  <td>{{ row.state }}</td>
                  <td class="text-right num">{{ row.count }}</td>
                  <td class="text-right num">{{ pct(row.count, total) }}</td>
                </tr>
              </tbody>
            </v-table>
          </template>
        </ChartPanel>

        <ChartPanel
          class="charts__city"
          title="Jobs by city"
          :subtitle="`${data.by_city.length} ${data.by_city.length === 1 ? 'city' : 'cities'}`"
        >
          <template #chart>
            <div :style="{ height: barHeight(cityRows) }">
              <Bar :data="barData(cityRows)" :options="barOptions" aria-label="Jobs by city bar chart" role="img" />
            </div>
          </template>
          <template #table>
            <v-table density="compact">
              <thead>
                <tr><th>City</th><th>State</th><th class="text-right">Jobs</th><th class="text-right">% of jobs</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in data.by_city" :key="`${row.city}-${row.state}`">
                  <td>{{ row.city }}</td>
                  <td>{{ row.state }}</td>
                  <td class="text-right num">{{ row.count }}</td>
                  <td class="text-right num">{{ pct(row.count, total) }}</td>
                </tr>
              </tbody>
            </v-table>
          </template>
        </ChartPanel>
      </div>
    </template>
  </div>
</template>

<style scoped>
.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 96px 0;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
}
.stat__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
}
.stat__value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.stat__label {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}
.charts__city {
  grid-column: 1 / -1;
}
@media (max-width: 900px) {
  .charts {
    grid-template-columns: minmax(0, 1fr);
  }
}
.donut-layout {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 24px;
}
.donut {
  position: relative;
  width: 220px;
  height: 220px;
}
.donut__center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.donut__value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
}
.donut__label {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.legend {
  list-style: none;
  padding: 0;
  margin: 0;
  min-width: 200px;
  flex: 0 1 240px;
}
.legend__item {
  display: grid;
  grid-template-columns: 12px 1fr auto auto;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 0.9rem;
}
.legend__item + .legend__item {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.legend__swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
}
.legend__name {
  font-weight: 500;
}
.legend__value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.legend__count {
  min-width: 28px;
  text-align: right;
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
  font-variant-numeric: tabular-nums;
}
.num {
  font-variant-numeric: tabular-nums;
}
</style>
