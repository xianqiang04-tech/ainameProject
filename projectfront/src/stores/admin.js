import { defineStore } from 'pinia'
import { adminApi } from '../api'
import { STORAGE_KEYS, clearSessionStorage, readStoredAdminProfile } from '../utils/storage'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    profile: readStoredAdminProfile(),
    checking: false,
  }),
  actions: {
    setProfile(profile) {
      this.profile = profile
      uni.setStorageSync(STORAGE_KEYS.adminProfile, profile)
    },
    async ensureAdmin(force = false) {
      if (this.profile && !force) return this.profile
      this.checking = true
      try {
        const profile = await adminApi.me()
        this.setProfile(profile)
        return profile
      } finally {
        this.checking = false
      }
    },
    clearProfile() {
      this.profile = null
      uni.removeStorageSync(STORAGE_KEYS.adminProfile)
    },
    logout() {
      clearSessionStorage()
      this.profile = null
    },
  },
})
