export const BACKEND_ORIGIN = 'http://127.0.0.1:8000'
export const API_BASE = import.meta.env.DEV ? '/api' : BACKEND_ORIGIN

export function resolveAssetUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return `${API_BASE}${url.startsWith('/') ? url : `/${url}`}`
}
