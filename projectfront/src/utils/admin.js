import { hasAccessToken } from './storage'

export async function requireAdminPage(adminStore) {
  if (!hasAccessToken()) {
    uni.reLaunch({ url: '/pages/admin/login' })
    return false
  }
  try {
    await adminStore.ensureAdmin()
    return true
  } catch (error) {
    if (error.statusCode === 403) {
      adminStore.logout()
      uni.showToast({ title: '当前账号没有管理员权限', icon: 'none' })
      setTimeout(() => uni.reLaunch({ url: '/pages/admin/login' }), 350)
    }
    return false
  }
}

export function formatDateTime(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  const pad = (part) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function formatMoney(value) {
  const number = Number(value)
  return Number.isFinite(number) ? `¥${number.toFixed(2)}` : '--'
}

export function normalizeInteger(value) {
  if (value === '' || value === null || value === undefined) return null
  const number = Number(value)
  return Number.isInteger(number) ? number : null
}
