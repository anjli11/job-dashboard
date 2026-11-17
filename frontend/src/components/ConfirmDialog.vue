<script setup>
defineProps({
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: 'Confirm' },
  loading: { type: Boolean, default: false },
})
const open = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])
</script>

<template>
  <v-dialog v-model="open" max-width="420" :persistent="loading">
    <v-card class="pa-2">
      <v-card-item>
        <template #prepend>
          <v-avatar color="error" variant="tonal" size="40"><v-icon icon="mdi-trash-can-outline" /></v-avatar>
        </template>
        <v-card-title class="confirm-title">{{ title }}</v-card-title>
      </v-card-item>
      <v-card-text class="text-muted">{{ message }}</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" :disabled="loading" @click="open = false">Cancel</v-btn>
        <v-btn color="error" variant="flat" :loading="loading" @click="emit('confirm')">{{ confirmText }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.confirm-title {
  font-weight: 600;
  white-space: normal;
}
</style>
