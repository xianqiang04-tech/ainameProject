import { defineStore } from 'pinia'
import { accountApi } from '../api'
import { STORAGE_KEYS, clearSessionStorage, readStoredUser } from '../utils/storage'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: readStoredUser(), balance: null, logoBalance: null }),
  actions: {
    setSession(session) {
      this.user = session.user
      uni.setStorageSync(STORAGE_KEYS.user, session.user)
      uni.setStorageSync(STORAGE_KEYS.accessToken, session.access_token)
      uni.setStorageSync(STORAGE_KEYS.refreshToken, session.refresh_token)
    },
    async refreshBalance() {
      const data = await accountApi.balance()
      this.balance = data.balance
      this.logoBalance = data.logo_balance
      return data.balance
    },
    logout() {
      clearSessionStorage()
      this.user = null
      this.balance = null
      this.logoBalance = null
    },
  },
})
