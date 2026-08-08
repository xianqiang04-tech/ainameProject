<template>
  <view class="brand-header">
    <view class="brand-lockup">
      <image class="brand-mark" src="/static/brand-mark.png" mode="aspectFill" />
      <view><text class="brand-name">智能起名</text><text class="brand-subtitle">为名字找到依据，也找到方向</text></view>
    </view>
    <button v-if="showBalance" class="balance-button" @click="openPackages">
      <WalletCards :size="17" :stroke-width="1.8" /><text>{{ balanceText }}</text><ChevronRight :size="16" :stroke-width="1.8" />
    </button>
  </view>
</template>
<script setup>
import { computed } from 'vue'
import { WalletCards, ChevronRight } from '@lucide/vue'
import { useAuthStore } from '../stores/auth'
defineProps({ showBalance: { type: Boolean, default: true } })
const authStore = useAuthStore()
const balanceText = computed(() => authStore.balance === null ? '查询额度' : `剩余 ${authStore.balance} 次`)
function openPackages() { uni.navigateTo({ url: '/pages/packages/packages' }) }
</script>
<style scoped>
.brand-header { display:flex; width:100%; max-width:1080px; min-height:94rpx; align-items:center; justify-content:space-between; gap:20rpx; margin:0 auto 28rpx; }
.brand-lockup { display:flex; min-width:0; align-items:center; gap:18rpx; }
.brand-mark { width:76rpx; height:76rpx; flex:0 0 auto; border:1px solid #dfe4e1; border-radius:7px; }
.brand-name { display:block; color:#18201c; font-size:32rpx; font-weight:750; line-height:1.2; }
.brand-subtitle { display:block; margin-top:5rpx; color:#77807c; font-size:21rpx; line-height:1.3; }
.balance-button { display:flex; min-height:64rpx; flex:0 0 auto; align-items:center; gap:8rpx; border:1px solid #cad5d0; border-radius:6px; background:#fff; padding:0 16rpx; color:#275e50; font-size:23rpx; }
@media (max-width:420px) { .brand-subtitle { display:none; } .brand-mark { width:68rpx; height:68rpx; } }
</style>
