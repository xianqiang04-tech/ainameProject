<template>
  <view class="auth-page">
    <view class="auth-shell">
      <view class="auth-intro">
        <image class="auth-mark" src="/static/brand-mark.png" mode="aspectFill" />
        <text class="auth-brand">智能起名</text>
        <text class="auth-title">让每个名字，都有清晰的来处。</text>
        <text class="auth-copy">结合命名要求、专属知识库和域名状态，快速得到可继续打磨的名字方案。</text>
        <view class="feature-list">
          <view><Check :size="17" /><text>人名、企业名、宠物名</text></view>
          <view><Check :size="17" /><text>结果可按意见持续调整</text></view>
          <view><Check :size="17" /><text>企业 Logo 同步生成</text></view>
        </view>
      </view>

      <view class="auth-form-wrap">
        <view class="auth-tabs">
          <button :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
          <button :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</button>
        </view>
        <view class="auth-form">
          <view class="form-heading">
            <text>{{ mode === 'login' ? '欢迎回来' : '创建你的账户' }}</text>
            <text>{{ mode === 'login' ? '登录后继续你的命名工作' : '注册成功即赠送 3 次起名额度' }}</text>
          </view>

          <view class="form-group">
            <text class="field-label">邮箱</text>
            <view class="input-with-icon"><Mail :size="19" /><input v-model.trim="form.email" class="input-control" type="text" placeholder="name@example.com" /></view>
          </view>
          <view v-if="mode === 'register'" class="form-group">
            <text class="field-label">用户名</text>
            <view class="input-with-icon"><UserRound :size="19" /><input v-model.trim="form.username" class="input-control" maxlength="10" placeholder="2–10 个字符" /></view>
          </view>
          <view class="form-group">
            <text class="field-label">密码</text>
            <view class="input-with-icon"><LockKeyhole :size="19" /><input v-model="form.password" class="input-control" password maxlength="10" placeholder="6–10 位密码" /></view>
          </view>
          <view v-if="mode === 'register'" class="form-group">
            <text class="field-label">确认密码</text>
            <view class="input-with-icon"><ShieldCheck :size="19" /><input v-model="form.confirmPassword" class="input-control" password maxlength="10" placeholder="再次输入密码" /></view>
          </view>
          <view v-if="mode === 'register'" class="form-group">
            <text class="field-label">邮箱验证码</text>
            <view class="code-row">
              <input v-model.trim="form.code" class="input-control" type="number" maxlength="4" placeholder="4 位验证码" />
              <button class="code-button" :disabled="countdown > 0 || codeLoading" @click="sendCode">
                {{ codeLoading ? '发送中' : countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </button>
            </view>
          </view>
          <button class="primary-button submit-button" :disabled="submitting" @click="submit">
            <LoaderCircle v-if="submitting" class="spin" :size="19" />
            <LogIn v-else :size="19" />
            <text>{{ submitting ? '处理中…' : mode === 'login' ? '登录' : '注册并登录' }}</text>
          </button>
          <view v-if="errorMessage" class="status-message error">{{ errorMessage }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { Check, Mail, UserRound, LockKeyhole, ShieldCheck, LogIn, LoaderCircle } from '@lucide/vue'
import { adminApi, authApi } from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useAdminStore } from '../../stores/admin'
import { hasAccessToken, readStoredUser } from '../../utils/storage'

const authStore = useAuthStore()
const adminStore = useAdminStore()
const mode = ref('login')
const submitting = ref(false)
const codeLoading = ref(false)
const countdown = ref(0)
const errorMessage = ref('')
let timer = null
const form = reactive({ email:'', username:'', password:'', confirmPassword:'', code:'' })

onLoad(async () => {
  if (hasAccessToken()) await enterMatchedHome(readStoredUser())
})
onUnload(() => clearInterval(timer))

async function enterMatchedHome(user) {
  // 兼容旧缓存中尚未保存 role 的管理员会话。
  if (user?.role === 'admin' || !user?.role) {
    try {
      const profile = await adminApi.me()
      adminStore.setProfile(profile)
      uni.reLaunch({ url:'/pages/admin/dashboard' })
      return
    } catch (error) {
      if (error.statusCode === 401) return
      if (error.statusCode !== 403) {
        errorMessage.value = error.message
        return
      }
    }
  }
  uni.reLaunch({ url:'/pages/naming/naming' })
}

function switchMode(value) { mode.value = value; errorMessage.value = '' }
function validEmail(value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) }
function validate() {
  if (!validEmail(form.email)) return '请输入正确的邮箱地址'
  if (mode.value === 'register' && (form.username.length < 2 || form.username.length > 10)) return '用户名需要 2–10 个字符'
  if (form.password.length < 6 || form.password.length > 10) return '密码需要 6–10 位'
  if (mode.value === 'register' && form.password !== form.confirmPassword) return '两次输入的密码不一致'
  if (mode.value === 'register' && !/^\d{4}$/.test(form.code)) return '请输入 4 位邮箱验证码'
  return ''
}
async function sendCode() {
  if (!validEmail(form.email)) return uni.showToast({ title:'请先输入正确邮箱', icon:'none' })
  codeLoading.value = true; errorMessage.value = ''
  try {
    await authApi.sendCode(form.email)
    uni.showToast({ title:'验证码已发送', icon:'success' })
    countdown.value = 60
    timer = setInterval(() => { countdown.value -= 1; if (countdown.value <= 0) clearInterval(timer) }, 1000)
  } catch (error) { errorMessage.value = error.message } finally { codeLoading.value = false }
}
async function submit() {
  const message = validate()
  if (message) { errorMessage.value = message; return }
  submitting.value = true; errorMessage.value = ''
  try {
    if (mode.value === 'register') {
      await authApi.register({ email:form.email, username:form.username, password:form.password, confirm_password:form.confirmPassword, code:form.code })
    }
    const session = await authApi.login({ email:form.email, password:form.password })
    authStore.setSession(session)
    await enterMatchedHome(session.user)
  } catch (error) { errorMessage.value = error.message } finally { submitting.value = false }
}
</script>

<style scoped>
.auth-page { min-height:100vh; display:flex; align-items:center; padding:40rpx 28rpx; background:#f4f6f5; }
.auth-shell { display:grid; width:100%; max-width:1080px; grid-template-columns:minmax(0,.9fr) minmax(400px,1fr); gap:64px; align-items:center; margin:0 auto; }
.auth-intro { padding:36rpx 8rpx; }
.auth-mark { width:96rpx; height:96rpx; border:1px solid #dbe2de; border-radius:8px; }
.auth-brand { display:block; margin-top:24rpx; color:#195e4d; font-size:28rpx; font-weight:700; }
.auth-title { display:block; max-width:600rpx; margin-top:30rpx; color:#18201c; font-size:58rpx; font-weight:760; line-height:1.28; }
.auth-copy { display:block; max-width:600rpx; margin-top:28rpx; color:#66716c; font-size:28rpx; line-height:1.8; }
.feature-list { margin-top:44rpx; color:#33413b; }
.feature-list view { display:flex; align-items:center; gap:14rpx; margin-top:18rpx; }
.feature-list svg { color:#16836b; }
.auth-form-wrap { overflow:hidden; border:1px solid #dce2df; border-radius:8px; background:#fff; box-shadow:0 18px 46px rgba(31,52,44,.08); }
.auth-tabs { display:grid; grid-template-columns:1fr 1fr; border-bottom:1px solid #e1e5e3; background:#f8faf9; padding:10rpx; }
.auth-tabs button { height:72rpx; border-radius:6px; background:transparent; color:#74807a; font-size:27rpx; }
.auth-tabs button.active { background:#fff; color:#126e58; font-weight:700; box-shadow:0 1px 4px rgba(28,47,40,.1); }
.auth-form { padding:42rpx; }
.form-heading > text:first-child { display:block; font-size:38rpx; font-weight:750; }
.form-heading > text:last-child { display:block; margin-top:8rpx; color:#7a837f; font-size:25rpx; }
.input-with-icon { position:relative; }
.input-with-icon svg { position:absolute; z-index:2; top:50%; left:22rpx; color:#78827d; transform:translateY(-50%); }
.input-with-icon .input-control { padding-left:70rpx; }
.code-row { display:grid; grid-template-columns:minmax(0,1fr) 210rpx; gap:14rpx; }
.code-button { min-height:88rpx; border:1px solid #b9cbc4; border-radius:6px; background:#edf6f2; color:#176b57; font-size:25rpx; }
.code-button[disabled] { color:#8a9892; }
.submit-button { width:100%; margin-top:38rpx; }
.spin { animation:spin .8s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
@media (max-width:760px) { .auth-page { align-items:flex-start; overflow-x:hidden; padding-top:70rpx; } .auth-shell { display:block; max-width:320px; } .auth-intro,.auth-form-wrap { min-width:0; max-width:100%; } .auth-intro { overflow:hidden; padding:0 8rpx 34rpx; } .auth-title,.auth-copy { overflow-wrap:anywhere; } .auth-title { margin-top:18rpx; font-size:42rpx; } .auth-copy { margin-top:16rpx; font-size:25rpx; } .feature-list { display:none; } .auth-mark { width:76rpx; height:76rpx; } .auth-form { padding:32rpx 28rpx; } }
</style>
