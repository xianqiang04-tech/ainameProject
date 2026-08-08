<template>
  <view class="admin-login-page">
    <view class="login-shell">
      <view class="login-brand">
        <image src="/static/brand-mark.png" mode="aspectFill" />
        <view><text>智能起名</text><text>管理控制台</text></view>
      </view>
      <view class="login-panel">
        <view class="login-heading"><ShieldCheck :size="28"/><text>管理员登录</text><text>使用已授权的管理员账号登录</text></view>
        <view class="login-field"><text>邮箱</text><view><Mail :size="18"/><input v-model.trim="form.email" type="text" placeholder="admin@example.com" @confirm="submit" /></view></view>
        <view class="login-field"><text>密码</text><view><LockKeyhole :size="18"/><input v-model="form.password" password maxlength="10" placeholder="请输入密码" @confirm="submit" /></view></view>
        <button class="login-button" :disabled="submitting" @click="submit">
          <LoaderCircle v-if="submitting" class="admin-spin" :size="19"/><LogIn v-else :size="19"/>
          <text>{{ submitting ? '正在验证' : '进入管理后台' }}</text>
        </button>
        <view v-if="errorMessage" class="admin-error">{{ errorMessage }}</view>
      </view>
      <text class="login-footnote">仅限授权人员访问</text>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { LoaderCircle, LockKeyhole, LogIn, Mail, ShieldCheck } from '@lucide/vue'
import { adminApi, authApi } from '../../api'
import { useAdminStore } from '../../stores/admin'
import { useAuthStore } from '../../stores/auth'
import { hasAccessToken } from '../../utils/storage'

const adminStore = useAdminStore()
const authStore = useAuthStore()
const form = reactive({ email: '', password: '' })
const submitting = ref(false)
const errorMessage = ref('')

onLoad(async () => {
  if (!hasAccessToken()) return
  try {
    const profile = await adminApi.me()
    adminStore.setProfile(profile)
    uni.reLaunch({ url: '/pages/admin/dashboard' })
  } catch (error) {
    if (error.statusCode === 403) {
      adminStore.logout()
      errorMessage.value = '当前登录账号没有管理员权限'
    }
  }
})

function validEmail(value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) }

async function submit() {
  if (submitting.value) return
  if (!validEmail(form.email)) { errorMessage.value = '请输入正确的邮箱地址'; return }
  if (form.password.length < 6 || form.password.length > 10) { errorMessage.value = '密码需要 6–10 位'; return }
  submitting.value = true
  errorMessage.value = ''
  try {
    const session = await authApi.login({ email: form.email, password: form.password })
    authStore.setSession(session)
    const profile = await adminApi.me()
    adminStore.setProfile(profile)
    uni.reLaunch({ url: '/pages/admin/dashboard' })
  } catch (error) {
    if (error.statusCode === 403) {
      adminStore.logout()
      errorMessage.value = '该账号没有管理员权限'
    } else {
      errorMessage.value = error.message
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.admin-login-page{display:flex;min-height:100vh;align-items:center;justify-content:center;background:#eef2f0;padding:28px}.login-shell{width:100%;max-width:430px}.login-brand{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:22px}.login-brand image{width:50px;height:50px;border:1px solid #d6deda;border-radius:8px}.login-brand view text:first-child{display:block;color:#1b2923;font-size:18px;font-weight:750}.login-brand view text:last-child{display:block;margin-top:3px;color:#6f7d76;font-size:12px}.login-panel{border:1px solid #d9e0dd;border-radius:8px;background:#fff;padding:30px;box-shadow:0 18px 48px rgba(27,46,38,.08)}.login-heading{display:flex;flex-direction:column;align-items:flex-start;color:#176f59}.login-heading>text:nth-child(2){margin-top:14px;color:#1c2521;font-size:22px;font-weight:750}.login-heading>text:last-child{margin-top:6px;color:#7a8580;font-size:12px}.login-field{margin-top:22px}.login-field>text{display:block;margin-bottom:8px;color:#485650;font-size:13px;font-weight:650}.login-field>view{position:relative}.login-field svg{position:absolute;z-index:2;top:50%;left:12px;color:#7c8882;transform:translateY(-50%)}.login-field input{height:44px;border:1px solid #cbd5d0;border-radius:6px;background:#fbfcfb;padding:0 12px 0 42px;color:#212a26;font-size:14px}.login-button{display:flex;width:100%;height:44px;align-items:center;justify-content:center;gap:9px;margin-top:28px;border-radius:6px;background:#167861;color:#fff;font-size:14px;font-weight:700}.login-button[disabled]{background:#91aea4}.login-footnote{display:block;margin-top:18px;color:#8a9690;font-size:11px;text-align:center}@media(max-width:480px){.admin-login-page{align-items:flex-start;padding:68px 20px 28px}.login-panel{padding:24px 20px}}
</style>
