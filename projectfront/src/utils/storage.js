export const STORAGE_KEYS = {
  accessToken: 'ai_name_access_token',
  refreshToken: 'ai_name_refresh_token',
  user: 'ai_name_user',
  adminProfile: 'ai_name_admin_profile',
}

export function readStoredUser() {
  return uni.getStorageSync(STORAGE_KEYS.user) || null
}

export function readStoredAdminProfile() {
  return uni.getStorageSync(STORAGE_KEYS.adminProfile) || null
}

export function clearSessionStorage() {
  Object.values(STORAGE_KEYS).forEach((key) => uni.removeStorageSync(key))
}

export function hasAccessToken() {
  return Boolean(uni.getStorageSync(STORAGE_KEYS.accessToken))
}

export function requireAuth() {
  if (hasAccessToken()) return true
  uni.reLaunch({ url: '/pages/auth/auth' })
  return false
}
