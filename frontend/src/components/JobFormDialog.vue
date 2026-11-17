<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useDisplay, useTheme } from 'vuetify'
import { createJob, parseApiError, updateJob } from '../api/jobs'
import { statusColor, useJobOptions } from '../composables/useJobOptions'
import ImageDropzone from './ImageDropzone.vue'
import RichTextEditor from './RichTextEditor.vue'

const props = defineProps({
  // The job being edited, or null when posting a new one.
  job: { type: Object, default: null },
})
const open = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['saved'])

const { smAndDown } = useDisplay()
const { statusOptions, categoryOptions } = useJobOptions()

const EMPTY = {
  title: '',
  statuses: [],
  categories: [],
  address: '',
  city: '',
  state: '',
  start_date: '',
  end_date: '',
  description: '',
}

const form = reactive({ ...EMPTY })
const imageFile = ref(null)
const imageRemoved = ref(false)
const formRef = ref(null)
const endDateRef = ref(null)
const saving = ref(false)
const serverErrors = ref({})
const generalError = ref('')

const isEdit = computed(() => Boolean(props.job))

function reset() {
  const source = props.job ?? EMPTY
  for (const key of Object.keys(EMPTY)) {
    const value = source[key] ?? EMPTY[key]
    form[key] = Array.isArray(value) ? [...value] : value
  }
  imageFile.value = null
  imageRemoved.value = false
  serverErrors.value = {}
  generalError.value = ''
  formRef.value?.resetValidation()
}

watch(open, (isOpen) => {
  if (isOpen) reset()
})

// Clear a field's server error as soon as the user edits it.
for (const key of Object.keys(EMPTY)) {
  watch(
    () => form[key],
    () => {
      if (serverErrors.value[key]) serverErrors.value = { ...serverErrors.value, [key]: undefined }
    },
  )
}
watch(imageFile, () => {
  if (serverErrors.value.image) serverErrors.value = { ...serverErrors.value, image: undefined }
})

const required = (label) => (v) => (Array.isArray(v) ? v.length > 0 : Boolean(String(v ?? '').trim())) || `${label} is required.`
const maxLength = (n) => (v) => !v || v.length <= n || `Must be ${n} characters or fewer.`

const rules = {
  title: [required('Job title'), maxLength(200)],
  statuses: [required('At least one status')],
  categories: [required('At least one category')],
  address: [maxLength(255)],
  city: [required('City'), maxLength(100)],
  state: [required('State'), maxLength(100)],
  start_date: [required('Start date')],
  end_date: [
    required('End date'),
    (v) => !v || !form.start_date || v >= form.start_date || 'End date cannot be before the start date.',
  ],
}

// Re-validate the end date when the start date moves.
watch(
  () => form.start_date,
  () => {
    if (form.end_date) endDateRef.value?.validate()
  },
)

async function submit() {
  generalError.value = ''
  const { valid } = await formRef.value.validate()
  if (!valid) {
    generalError.value = 'Please fix the highlighted fields.'
    return
  }

  saving.value = true
  try {
    const files = { image: imageFile.value, removeImage: imageRemoved.value }
    const saved = isEdit.value ? await updateJob(props.job.id, form, files) : await createJob(form, files)
    emit('saved', saved, { created: !isEdit.value })
    open.value = false
  } catch (error) {
    const { general, fields } = parseApiError(error)
    serverErrors.value = fields
    generalError.value = general
  } finally {
    saving.value = false
  }
}

const theme = useTheme()
const statusDotColor = (value) => statusColor(value, theme.global.current.value.dark)
</script>

<template>
  <v-dialog v-model="open" :fullscreen="smAndDown" max-width="780" scrollable :persistent="saving">
    <v-card :rounded="smAndDown ? 0 : 'lg'">
      <v-card-item class="dialog-header">
        <v-card-title class="dialog-title">{{ isEdit ? 'Edit job' : 'Post a new job' }}</v-card-title>
        <v-card-subtitle>{{ isEdit ? 'Update the details for this posting.' : 'Fill in the details below to publish a job.' }}</v-card-subtitle>
        <template #append>
          <v-btn icon="mdi-close" variant="text" aria-label="Close" :disabled="saving" @click="open = false" />
        </template>
      </v-card-item>
      <v-divider />

      <v-card-text class="dialog-body">
        <v-alert
          v-if="generalError"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-4"
          :text="generalError"
        />

        <v-form ref="formRef" validate-on="input lazy" @submit.prevent="submit">
          <section class="form-section">
            <label class="section-label">Job profile picture</label>
            <ImageDropzone
              v-model="imageFile"
              v-model:removed="imageRemoved"
              :existing-url="job?.image || null"
              :error-message="serverErrors.image"
            />
          </section>

          <section class="form-section">
            <v-text-field
              v-model="form.title"
              label="Job title *"
              placeholder="e.g. Senior Backend Engineer"
              :rules="rules.title"
              :error-messages="serverErrors.title"
              counter="200"
              autofocus
            />

            <div class="grid-2">
              <v-select
                v-model="form.statuses"
                :items="statusOptions"
                item-title="label"
                item-value="value"
                label="Status *"
                multiple
                chips
                closable-chips
                :rules="rules.statuses"
                :error-messages="serverErrors.statuses"
              >
                <template #chip="{ item, props: chipProps }">
                  <v-chip v-bind="chipProps" size="small">
                    <template #prepend>
                      <span class="chip-dot" :style="{ background: statusDotColor(item.value) }" />
                    </template>
                    {{ item.label }}
                  </v-chip>
                </template>
              </v-select>
              <v-select
                v-model="form.categories"
                :items="categoryOptions"
                item-title="label"
                item-value="value"
                label="Job category *"
                multiple
                chips
                closable-chips
                :rules="rules.categories"
                :error-messages="serverErrors.categories"
              />
            </div>
          </section>

          <section class="form-section">
            <label class="section-label">Location</label>
            <v-text-field
              v-model="form.address"
              label="Address"
              placeholder="Street address"
              prepend-inner-icon="mdi-map-marker-outline"
              :rules="rules.address"
              :error-messages="serverErrors.address"
            />
            <div class="grid-2">
              <v-text-field
                v-model="form.city"
                label="City *"
                :rules="rules.city"
                :error-messages="serverErrors.city"
              />
              <v-text-field
                v-model="form.state"
                label="State *"
                :rules="rules.state"
                :error-messages="serverErrors.state"
              />
            </div>
          </section>

          <section class="form-section">
            <label class="section-label">Duration</label>
            <div class="grid-2">
              <v-text-field
                v-model="form.start_date"
                type="date"
                label="Start date *"
                :rules="rules.start_date"
                :error-messages="serverErrors.start_date"
              />
              <v-text-field
                ref="endDateRef"
                v-model="form.end_date"
                type="date"
                label="End date *"
                :min="form.start_date || undefined"
                :rules="rules.end_date"
                :error-messages="serverErrors.end_date"
              />
            </div>
          </section>

          <section class="form-section">
            <label class="section-label">Description</label>
            <RichTextEditor
              v-model="form.description"
              placeholder="Describe the role, responsibilities and requirements…"
              :error-message="serverErrors.description"
            />
          </section>

          <!-- Lets Enter submit from text inputs. -->
          <button type="submit" hidden />
        </v-form>
      </v-card-text>

      <v-divider />
      <v-card-actions class="dialog-actions">
        <v-spacer />
        <v-btn variant="text" :disabled="saving" @click="open = false">Cancel</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="submit">
          {{ isEdit ? 'Save changes' : 'Post job' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.dialog-header {
  padding: 18px 20px 14px;
}
.dialog-title {
  font-weight: 700;
  font-size: 1.2rem;
}
.dialog-body {
  padding: 20px !important;
}
.dialog-actions {
  padding: 12px 20px;
}
.form-section + .form-section {
  margin-top: 8px;
}
.form-section {
  margin-bottom: 8px;
}
.section-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 10px;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}
@media (max-width: 600px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
</style>
