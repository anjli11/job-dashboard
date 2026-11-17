import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'

export const THEME_STORAGE_KEY = 'jobboard-theme'

function initialTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    // Storage can be unavailable (private mode); fall back to the OS preference.
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default createVuetify({
  theme: {
    defaultTheme: initialTheme(),
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#f6f6f4',
          surface: '#ffffff',
          'surface-variant': '#eeeeea',
          primary: '#4f46e5',
          secondary: '#52514e',
          error: '#d03b3b',
          success: '#0ca30c',
          warning: '#c98500',
          info: '#2a78d6',
        },
      },
      dark: {
        dark: true,
        colors: {
          background: '#0f0f0f',
          surface: '#1a1a19',
          'surface-variant': '#2c2c2a',
          primary: '#8b85f0',
          secondary: '#c3c2b7',
          error: '#e66767',
          success: '#0ca30c',
          warning: '#fab219',
          info: '#3987e5',
        },
      },
    },
  },
  defaults: {
    VTextField: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VTextarea: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VSelect: { variant: 'outlined', density: 'comfortable', color: 'primary' },
    VBtn: { style: 'text-transform: none; letter-spacing: 0;' },
    VCard: { rounded: 'lg' },
  },
})
