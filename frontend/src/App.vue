<script setup>
import { computed } from 'vue'
import { useTheme } from 'vuetify'
import { THEME_STORAGE_KEY } from './plugins/vuetify'

const theme = useTheme()
const isDark = computed(() => theme.global.current.value.dark)

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  theme.change(next)
  try {
    localStorage.setItem(THEME_STORAGE_KEY, next)
  } catch {
    // Non-essential preference; ignore storage failures.
  }
}
</script>

<template>
  <v-app>
    <v-app-bar flat border="b" color="surface" height="64">
      <div class="app-bar-inner">
        <router-link to="/" class="brand">
          <span class="brand-mark"><v-icon icon="mdi-briefcase-variant" size="18" /></span>
          <span class="brand-name">JobBoard</span>
        </router-link>

        <nav class="nav">
          <v-btn :to="{ name: 'jobs' }" variant="text" prepend-icon="mdi-view-grid-outline">
            <span class="nav-label">Jobs</span>
          </v-btn>
          <v-btn :to="{ name: 'analytics' }" variant="text" prepend-icon="mdi-chart-donut">
            <span class="nav-label">Analytics</span>
          </v-btn>
        </nav>

        <v-btn
          :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
          @click="toggleTheme"
        />
      </div>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<style scoped>
.app-bar-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: inherit;
  text-decoration: none;
  margin-right: auto;
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
}
.brand-name {
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}
.nav {
  display: flex;
  gap: 4px;
}
@media (max-width: 520px) {
  .nav-label {
    display: none;
  }
  .nav :deep(.v-btn__prepend) {
    margin-inline: 0;
  }
}
</style>
