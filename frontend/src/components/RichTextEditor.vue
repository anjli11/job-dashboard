<script setup>
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  errorMessage: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

function normalize(html) {
  // An empty editor still serializes to "<p></p>".
  return html === '<p></p>' ? '' : html
}

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      heading: { levels: [2, 3] },
      // The backend sanitizer strips attributes, so links would lose their href.
      link: false,
      horizontalRule: false,
      codeBlock: false,
    }),
  ],
  editorProps: {
    attributes: { class: 'rte__content', 'aria-label': 'Job description', role: 'textbox', 'aria-multiline': 'true' },
  },
  onUpdate: ({ editor: ed }) => emit('update:modelValue', normalize(ed.getHTML())),
})

watch(
  () => props.modelValue,
  (value) => {
    const ed = editor.value
    if (!ed || normalize(ed.getHTML()) === (value || '')) return
    ed.commands.setContent(value || '', { emitUpdate: false })
  },
)

onBeforeUnmount(() => editor.value?.destroy())

const tools = [
  { icon: 'mdi-format-bold', label: 'Bold', name: 'bold', run: (c) => c.toggleBold() },
  { icon: 'mdi-format-italic', label: 'Italic', name: 'italic', run: (c) => c.toggleItalic() },
  { icon: 'mdi-format-underline', label: 'Underline', name: 'underline', run: (c) => c.toggleUnderline() },
  { icon: 'mdi-format-strikethrough', label: 'Strikethrough', name: 'strike', run: (c) => c.toggleStrike() },
  { divider: true },
  { icon: 'mdi-format-header-2', label: 'Heading', name: 'heading', attrs: { level: 2 }, run: (c) => c.toggleHeading({ level: 2 }) },
  { icon: 'mdi-format-list-bulleted', label: 'Bullet list', name: 'bulletList', run: (c) => c.toggleBulletList() },
  { icon: 'mdi-format-list-numbered', label: 'Numbered list', name: 'orderedList', run: (c) => c.toggleOrderedList() },
  { icon: 'mdi-format-quote-close', label: 'Quote', name: 'blockquote', run: (c) => c.toggleBlockquote() },
]

function apply(tool) {
  tool.run(editor.value.chain().focus()).run()
}
</script>

<template>
  <div>
  <div class="rte" :class="{ 'rte--error': errorMessage }">
    <div v-if="editor" class="rte__toolbar" role="toolbar" aria-label="Formatting">
      <template v-for="(tool, i) in tools" :key="i">
        <v-divider v-if="tool.divider" vertical class="mx-1 my-1" />
        <v-btn
          v-else
          :icon="tool.icon"
          size="small"
          density="comfortable"
          variant="text"
          :color="editor.isActive(tool.name, tool.attrs) ? 'primary' : undefined"
          :aria-label="tool.label"
          :aria-pressed="editor.isActive(tool.name, tool.attrs)"
          @click="apply(tool)"
        />
      </template>
      <v-spacer />
      <v-btn
        icon="mdi-undo"
        size="small"
        density="comfortable"
        variant="text"
        aria-label="Undo"
        :disabled="!editor.can().undo()"
        @click="editor.chain().focus().undo().run()"
      />
      <v-btn
        icon="mdi-redo"
        size="small"
        density="comfortable"
        variant="text"
        aria-label="Redo"
        :disabled="!editor.can().redo()"
        @click="editor.chain().focus().redo().run()"
      />
    </div>
    <div class="rte__body">
      <EditorContent :editor="editor" />
      <div v-if="editor && editor.isEmpty && placeholder" class="rte__placeholder">{{ placeholder }}</div>
    </div>
  </div>
  <div v-if="errorMessage" class="rte__error" role="alert">{{ errorMessage }}</div>
  </div>
</template>

<style scoped>
.rte {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.38);
  border-radius: 4px;
  transition: border-color 0.15s ease;
}
.rte:focus-within {
  border-color: rgb(var(--v-theme-primary));
  box-shadow: 0 0 0 1px rgb(var(--v-theme-primary));
}
.rte--error {
  border-color: rgb(var(--v-theme-error));
}
.rte__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  padding: 4px 6px;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.12);
}
.rte__body {
  position: relative;
}
.rte__placeholder {
  position: absolute;
  top: 12px;
  left: 14px;
  pointer-events: none;
  color: rgba(var(--v-theme-on-surface), 0.45);
  font-size: 0.95rem;
}
.rte__body :deep(.rte__content) {
  min-height: 140px;
  max-height: 320px;
  overflow-y: auto;
  padding: 12px 14px;
  outline: none;
  font-size: 0.95rem;
  line-height: 1.55;
}
.rte__body :deep(.rte__content > * + *) {
  margin-top: 0.5em;
}
.rte__body :deep(.rte__content ul),
.rte__body :deep(.rte__content ol) {
  padding-left: 1.4em;
}
.rte__body :deep(.rte__content h2) {
  font-size: 1.15rem;
  font-weight: 600;
}
.rte__body :deep(.rte__content blockquote) {
  border-left: 3px solid rgba(var(--v-theme-on-surface), 0.2);
  padding-left: 12px;
  color: rgba(var(--v-theme-on-surface), 0.75);
}
.rte__error {
  margin-top: 6px;
  padding-left: 16px;
  font-size: 0.75rem;
  color: rgb(var(--v-theme-error));
}
</style>
