<script setup>
defineProps({
  icon: { type: String, default: 'mdi-briefcase-search-outline' },
  title: { type: String, required: true },
  message: { type: String, default: '' },
})
</script>

<template>
  <div class="empty panel">
    <div class="empty__icon">
      <v-icon :icon="icon" size="40" />
    </div>
    <h2 class="empty__title">{{ title }}</h2>
    <p v-if="message" class="empty__message">{{ message }}</p>
    <div class="empty__actions"><slot /></div>
  </div>
</template>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 64px 24px;
}
.empty__icon {
  display: grid;
  place-items: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
  margin-bottom: 20px;
}
.empty__title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}
.empty__message {
  margin: 8px 0 0;
  max-width: 420px;
  color: rgba(var(--v-theme-on-surface), 0.62);
}
.empty__actions {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}
</style>
