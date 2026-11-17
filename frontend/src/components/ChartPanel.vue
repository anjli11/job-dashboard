<script setup>
import { ref } from 'vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})

const view = ref('chart')
</script>

<template>
  <section class="chart-panel panel">
    <header class="chart-panel__header">
      <div>
        <h2 class="chart-panel__title">{{ title }}</h2>
        <p v-if="subtitle" class="chart-panel__subtitle">{{ subtitle }}</p>
      </div>
      <v-btn-toggle v-model="view" mandatory density="compact" variant="outlined" divided rounded="lg">
        <v-btn value="chart" icon="mdi-chart-bar" size="small" :aria-label="`${title}: chart view`" />
        <v-btn value="table" icon="mdi-table" size="small" :aria-label="`${title}: table view`" />
      </v-btn-toggle>
    </header>
    <div class="chart-panel__body">
      <slot v-if="view === 'chart'" name="chart" />
      <slot v-else name="table" />
    </div>
  </section>
</template>

<style scoped>
.chart-panel {
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-width: 0;
}
.chart-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}
.chart-panel__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}
.chart-panel__subtitle {
  margin: 2px 0 0;
  font-size: 0.82rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.chart-panel__body {
  flex: 1;
  min-height: 0;
}
</style>
