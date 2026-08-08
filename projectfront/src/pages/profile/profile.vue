<template>
  <view class="page-shell">
    <BrandHeader />
    <view class="page-content profile-layout">
      <view class="profile-main">
        <view class="panel identity-panel">
          <view class="avatar"><UserRound :size="30" /></view>
          <view class="identity"><text>{{authStore.user?.username||'用户'}}</text><text>{{authStore.user?.email||'--'}}</text></view>
        </view>
        <view class="balance-panel">
          <view class="balance-stats">
            <view><text>剩余起名额度</text><text>{{authStore.balance===null?'--':authStore.balance}}</text><text>次</text></view>
            <view><text>剩余 Logo 次数</text><text>{{authStore.logoBalance===null?'--':authStore.logoBalance}}</text><text>次</text></view>
          </view>
          <button @click="openPackages"><ShoppingBag :size="18"/><text>购买套餐</text><ChevronRight :size="16"/></button>
        </view>
      </view>
      <view class="settings-column">
        <view class="panel settings-panel">
          <text class="settings-title">账户</text>
          <button class="setting-row" @click="refreshBalance"><RefreshCw :class="{spin:refreshing}" :size="19"/><view><text>刷新额度</text><text>从后端重新读取当前可用次数</text></view><ChevronRight :size="17"/></button>
          <button class="setting-row" @click="testEmail"><MailCheck :size="19"/><view><text>邮件服务自检</text><text>会向后端代码中固定的测试邮箱发送邮件</text></view><ChevronRight :size="17"/></button>
        </view>
        <button class="danger-button logout-button" @click="confirmLogout"><LogOut :size="18"/><text>退出登录</text></button>
        <text class="version">智能起名 H5 · v1.0.0</text>
      </view>
    </view>
    <BottomNav active="profile" />
  </view>
</template>

<script setup>
import {ref} from 'vue'; import {onShow} from '@dcloudio/uni-app'; import {UserRound,ShoppingBag,ChevronRight,RefreshCw,MailCheck,LogOut} from '@lucide/vue'
import BrandHeader from '../../components/BrandHeader.vue'; import BottomNav from '../../components/BottomNav.vue'; import {useAuthStore} from '../../stores/auth'; import {requireAuth} from '../../utils/storage'; import {accountApi} from '../../api'
const authStore=useAuthStore(); const refreshing=ref(false)
onShow(async()=>{if(!requireAuth())return;await refreshBalance(false)})
function openPackages(){uni.navigateTo({url:'/pages/packages/packages'})}
async function refreshBalance(show=true){refreshing.value=true;try{await authStore.refreshBalance();if(show)uni.showToast({title:'额度已更新',icon:'none'})}catch(error){if(show)uni.showToast({title:error.message,icon:'none'})}finally{refreshing.value=false}}
function testEmail(){uni.showModal({title:'确认发送测试邮件',content:'此操作会调用后端 /email，并向后端代码中固定的测试邮箱发送一封邮件。',confirmText:'确认发送',success:async({confirm})=>{if(!confirm)return;uni.showLoading({title:'发送中'});try{const data=await accountApi.sendTestEmail();uni.showToast({title:data.message||'邮件已发送',icon:'none',duration:2500})}catch(error){uni.showToast({title:error.message,icon:'none',duration:2500})}finally{uni.hideLoading()}}})}
function confirmLogout(){uni.showModal({title:'退出登录',content:'退出后需要重新输入邮箱和密码。',confirmColor:'#b74638',success:({confirm})=>{if(confirm){authStore.logout();uni.reLaunch({url:'/pages/auth/auth'})}}})}
</script>

<style scoped>
.profile-layout{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:28rpx;align-items:start}.identity-panel{display:flex;align-items:center;gap:22rpx}.avatar{display:flex;width:88rpx;height:88rpx;align-items:center;justify-content:center;border-radius:8px;background:#e8f3ef;color:#176f59}.identity{min-width:0}.identity text:first-child{display:block;font-size:32rpx;font-weight:750}.identity text:last-child{display:block;overflow:hidden;margin-top:8rpx;color:#75807a;font-size:23rpx;text-overflow:ellipsis;white-space:nowrap}.balance-panel{overflow:hidden;margin-top:20rpx;border-radius:8px;background:#1d2d27;color:#fff}.balance-stats{display:flex}.balance-stats>view{flex:1;padding:34rpx}.balance-stats>view text:first-child{display:block;color:#b9c9c2;font-size:24rpx}.balance-stats>view text:nth-child(2){font-size:64rpx;font-weight:760;line-height:1.25}.balance-stats>view text:last-child{margin-left:8rpx;color:#b9c9c2;font-size:24rpx}.balance-panel button{display:flex;width:100%;min-height:78rpx;align-items:center;gap:10rpx;border-radius:0;background:#27473c;padding:0 24rpx;color:#e9f3ef;font-size:25rpx}.balance-panel button text{flex:1;text-align:left}.settings-panel{padding:12rpx 28rpx}.settings-title{display:block;padding:20rpx 8rpx 14rpx;color:#77817c;font-size:23rpx}.setting-row{display:flex;width:100%;min-height:112rpx;align-items:center;gap:18rpx;border-top:1px solid #edf0ee;border-radius:0;background:#fff;padding:16rpx 8rpx;color:#4a5a53;text-align:left}.setting-row>view{min-width:0;flex:1}.setting-row>view text:first-child{display:block;color:#26312c;font-size:27rpx;font-weight:650}.setting-row>view text:last-child{display:block;margin-top:6rpx;color:#89918d;font-size:21rpx;line-height:1.45}.logout-button{width:100%;margin-top:20rpx}.version{display:block;margin-top:28rpx;color:#9aa19e;font-size:21rpx;text-align:center}.spin{animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}@media(max-width:760px){.profile-layout{display:block}.settings-column{margin-top:22rpx}}
</style>
