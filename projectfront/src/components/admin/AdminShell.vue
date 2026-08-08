<template>
  <view class="admin-shell">
    <view v-if="menuOpen" class="mobile-mask" @click="menuOpen = false" />
    <view class="admin-sidebar" :class="{ open: menuOpen }">
      <view class="sidebar-brand">
        <image src="/static/brand-mark.png" mode="aspectFill" />
        <view><text>智能起名</text><text>管理控制台</text></view>
        <button class="close-menu" aria-label="关闭菜单" @click="menuOpen = false"><X :size="20" /></button>
      </view>

      <view class="sidebar-nav">
        <button v-for="item in navItems" :key="item.key" :class="{ active: active === item.key }" @click="go(item)">
          <component :is="item.icon" :size="19" :stroke-width="active === item.key ? 2.2 : 1.8" />
          <text>{{ item.label }}</text>
          <ChevronRight v-if="active === item.key" :size="15" />
        </button>
      </view>

      <view class="sidebar-account">
        <view class="admin-avatar"><ShieldCheck :size="20" /></view>
        <view class="account-copy">
          <text>{{ adminStore.profile?.username || '管理员' }}</text>
          <text>{{ adminStore.profile?.email || '--' }}</text>
        </view>
        <button aria-label="退出登录" @click="confirmLogout"><LogOut :size="18" /></button>
      </view>
    </view>

    <view class="admin-workspace">
      <view class="mobile-header">
        <button aria-label="打开菜单" @click="menuOpen = true"><Menu :size="22" /></button>
        <view><text>管理控制台</text><text>{{ title }}</text></view>
        <view class="mobile-header-spacer" />
      </view>
      <view class="admin-topbar">
        <view class="topbar-title"><text>{{ title }}</text><text>{{ subtitle }}</text></view>
        <view class="topbar-actions"><slot name="actions" /></view>
      </view>
      <view class="admin-content"><slot /></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { BarChart3, ChevronRight, ClipboardList, LogOut, Menu, Package, ScrollText, ShieldCheck, Users, X } from '@lucide/vue'
import { useAdminStore } from '../../stores/admin'

const props = defineProps({
  active: { type: String, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
const adminStore = useAdminStore()
const menuOpen = ref(false)
const navItems = [
  { key: 'dashboard', label: '概览', icon: BarChart3, url: '/pages/admin/dashboard' },
  { key: 'users', label: '用户管理', icon: Users, url: '/pages/admin/users' },
  { key: 'packages', label: '套餐管理', icon: Package, url: '/pages/admin/packages' },
  { key: 'orders', label: '订单查询', icon: ClipboardList, url: '/pages/admin/orders' },
  { key: 'audit', label: '审计日志', icon: ScrollText, url: '/pages/admin/audit' },
]

function go(item) {
  menuOpen.value = false
  if (item.key !== props.active) uni.redirectTo({ url: item.url })
}

function confirmLogout() {
  uni.showModal({
    title: '退出管理后台',
    content: '退出后需要重新输入管理员邮箱和密码。',
    confirmColor: '#b74638',
    success: ({ confirm }) => {
      if (!confirm) return
      adminStore.logout()
      uni.reLaunch({ url: '/pages/admin/login' })
    },
  })
}
</script>

<style scoped>
.admin-shell{min-height:100vh;background:#f3f5f4;color:#202723}.admin-sidebar{position:fixed;z-index:50;top:0;bottom:0;left:0;display:flex;width:244px;flex-direction:column;border-right:1px solid #dfe4e1;background:#17231f;color:#eaf0ed}.sidebar-brand{display:flex;min-height:92px;align-items:center;gap:12px;border-bottom:1px solid rgba(255,255,255,.09);padding:18px 20px}.sidebar-brand image{width:44px;height:44px;flex:0 0 auto;border:1px solid rgba(255,255,255,.14);border-radius:7px}.sidebar-brand view{min-width:0}.sidebar-brand view text:first-child{display:block;font-size:16px;font-weight:700}.sidebar-brand view text:last-child{display:block;margin-top:3px;color:#91a39b;font-size:12px}.close-menu{display:none}.sidebar-nav{flex:1;padding:18px 12px}.sidebar-nav button{display:flex;width:100%;height:46px;align-items:center;gap:12px;margin-bottom:5px;border-radius:6px;background:transparent;padding:0 13px;color:#aebdb7;font-size:14px;text-align:left}.sidebar-nav button text{flex:1}.sidebar-nav button.active{background:#25463b;color:#fff}.sidebar-account{display:flex;align-items:center;gap:10px;border-top:1px solid rgba(255,255,255,.09);padding:16px}.admin-avatar{display:flex;width:36px;height:36px;flex:0 0 auto;align-items:center;justify-content:center;border-radius:6px;background:#244a3d;color:#bfe0d4}.account-copy{min-width:0;flex:1}.account-copy text:first-child{display:block;font-size:13px;font-weight:650}.account-copy text:last-child{display:block;overflow:hidden;margin-top:3px;color:#91a39b;font-size:11px;text-overflow:ellipsis;white-space:nowrap}.sidebar-account button{display:flex;width:34px;height:34px;align-items:center;justify-content:center;border-radius:6px;background:transparent;color:#aebdb7}.admin-workspace{min-height:100vh;margin-left:244px}.admin-topbar{display:flex;min-height:92px;align-items:center;justify-content:space-between;gap:24px;border-bottom:1px solid #dfe4e1;background:#fff;padding:20px 32px}.topbar-title text:first-child{display:block;color:#18201c;font-size:24px;font-weight:720}.topbar-title text:last-child{display:block;margin-top:5px;color:#74807a;font-size:13px}.topbar-actions{display:flex;align-items:center;gap:10px}.admin-content{padding:28px 32px 48px}.mobile-header,.mobile-mask{display:none}
@media(max-width:760px){.admin-sidebar{width:280px;max-width:84vw;transform:translateX(-102%);transition:transform .2s ease}.admin-sidebar.open{transform:translateX(0)}.mobile-mask{position:fixed;z-index:45;inset:0;display:block;background:rgba(18,27,23,.42)}.close-menu{display:flex;width:34px;height:34px;align-items:center;justify-content:center;margin-left:auto;border-radius:6px;background:transparent;color:#afbeb8}.admin-workspace{margin-left:0}.mobile-header{display:flex;height:64px;align-items:center;gap:12px;border-bottom:1px solid #dfe4e1;background:#fff;padding:0 16px}.mobile-header>button{display:flex;width:38px;height:38px;align-items:center;justify-content:center;border:1px solid #d6deda;border-radius:6px;background:#fff;color:#31413a}.mobile-header>view:nth-child(2){min-width:0;flex:1}.mobile-header text:first-child{display:block;color:#63706a;font-size:11px}.mobile-header text:last-child{display:block;overflow:hidden;margin-top:2px;color:#1b2420;font-size:16px;font-weight:700;text-overflow:ellipsis;white-space:nowrap}.mobile-header-spacer{width:38px}.admin-topbar{min-height:auto;border-bottom:0;background:transparent;padding:22px 18px 12px}.topbar-title text:first-child{font-size:21px}.topbar-title text:last-child{font-size:12px;line-height:1.5}.topbar-actions{align-self:flex-start}.admin-content{padding:8px 18px 36px}}
</style>
