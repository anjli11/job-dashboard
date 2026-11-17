export function stripHtml(html) {
  if (!html) return ''
  const doc = new DOMParser().parseFromString(html, 'text/html')
  // Keep word boundaries between block elements (e.g. list items) when flattening.
  doc.querySelectorAll('p, li, h2, h3, blockquote, br').forEach((el) => el.append(' '))
  return (doc.body.textContent || '').replace(/\s+/g, ' ').trim()
}

const dateFormatter = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' })

export function formatDate(isoDate) {
  if (!isoDate) return ''
  // Parse as a local calendar date; `new Date('2026-01-01')` would be UTC midnight.
  const [y, m, d] = isoDate.split('-').map(Number)
  return dateFormatter.format(new Date(y, m - 1, d))
}

export function formatDateRange(start, end) {
  if (!start && !end) return ''
  return `${formatDate(start)} – ${formatDate(end)}`
}
