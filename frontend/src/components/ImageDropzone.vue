<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const MAX_BYTES = 5 * 1024 * 1024
const ACCEPTED = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

const props = defineProps({
  // URL of the image already stored on the server (edit mode).
  existingUrl: { type: String, default: null },
  // The newly picked File, if any.
  modelValue: { type: File, default: null },
  removed: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'update:removed'])

const input = ref(null)
const dragging = ref(false)
const localError = ref('')
const objectUrl = ref(null)

watch(
  () => props.modelValue,
  (file) => {
    if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = file ? URL.createObjectURL(file) : null
  },
  { immediate: true },
)
onBeforeUnmount(() => {
  if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
})

const previewUrl = computed(() => objectUrl.value || (!props.removed ? props.existingUrl : null))
const error = computed(() => localError.value || props.errorMessage)

function accept(file) {
  localError.value = ''
  if (!file) return
  if (!ACCEPTED.includes(file.type)) {
    localError.value = 'Upload a JPEG, PNG, GIF or WebP image.'
    return
  }
  if (file.size > MAX_BYTES) {
    localError.value = 'Image must be 5 MB or smaller.'
    return
  }
  emit('update:modelValue', file)
  emit('update:removed', false)
}

function onDrop(event) {
  dragging.value = false
  accept(event.dataTransfer?.files?.[0])
}

function onPick(event) {
  accept(event.target.files?.[0])
  event.target.value = ''
}

function clear() {
  localError.value = ''
  emit('update:modelValue', null)
  if (props.existingUrl) emit('update:removed', true)
}

function browse() {
  input.value?.click()
}
</script>

<template>
  <div>
    <div
      class="dropzone"
      :class="{ 'dropzone--active': dragging, 'dropzone--error': error, 'dropzone--filled': previewUrl }"
      role="button"
      tabindex="0"
      aria-label="Upload job profile picture"
      @click="browse"
      @keydown.enter.prevent="browse"
      @keydown.space.prevent="browse"
      @dragenter.prevent="dragging = true"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <template v-if="previewUrl">
        <img :src="previewUrl" alt="Selected job picture preview" class="dropzone__preview" />
        <div class="dropzone__overlay">
          <v-btn size="small" variant="flat" prepend-icon="mdi-swap-horizontal" @click.stop="browse">Replace</v-btn>
          <v-btn size="small" variant="flat" color="error" prepend-icon="mdi-close" @click.stop="clear">Remove</v-btn>
        </div>
      </template>
      <div v-else class="dropzone__empty">
        <v-icon icon="mdi-image-plus-outline" size="36" class="mb-2" />
        <div class="dropzone__title">
          <strong>Drag &amp; drop</strong> an image here, or <span class="dropzone__link">browse</span>
        </div>
        <div class="dropzone__hint">JPEG, PNG, GIF or WebP · up to 5 MB</div>
      </div>
      <input ref="input" type="file" :accept="ACCEPTED.join(',')" hidden @change="onPick" />
    </div>
    <div v-if="error" class="dropzone__error" role="alert">{{ error }}</div>
  </div>
</template>

<style scoped>
.dropzone {
  position: relative;
  display: grid;
  place-items: center;
  height: 180px;
  border: 2px dashed rgba(var(--v-theme-on-surface), 0.22);
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.025);
  cursor: pointer;
  overflow: hidden;
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
  outline: none;
}
.dropzone:hover,
.dropzone:focus-visible,
.dropzone--active {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.06);
}
.dropzone--error {
  border-color: rgb(var(--v-theme-error));
}
.dropzone--filled {
  border-style: solid;
}
.dropzone__empty {
  text-align: center;
  padding: 16px;
  color: rgba(var(--v-theme-on-surface), 0.7);
}
.dropzone__title {
  font-size: 0.9rem;
}
.dropzone__link {
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
  text-decoration: underline;
}
.dropzone__hint {
  margin-top: 4px;
  font-size: 0.78rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}
.dropzone__preview {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.dropzone__overlay {
  position: absolute;
  right: 10px;
  bottom: 10px;
  display: flex;
  gap: 8px;
}
.dropzone__error {
  margin-top: 6px;
  padding-left: 16px;
  font-size: 0.75rem;
  color: rgb(var(--v-theme-error));
}
</style>
