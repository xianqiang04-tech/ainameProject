<template>
  <view class="packages-page page-shell">
    <view class="packages-header page-content">
      <button class="back-button" title="返回" @click="goBack"><ArrowLeft :size="21"/></button>
      <view><text class="section-title">选择起名套餐</text><text class="section-note">购买成功后，起名额度会自动加入当前账户。</text></view>
      <view class="current-balance"><text>当前额度</text><text>{{authStore.balance===null?'--':authStore.balance}} 次</text></view>
    </view>
    <view class="page-content">
      <view v-if="loading" class="loading-panel"><LoaderCircle class="spin" :size="32"/><text>正在读取套餐…</text></view>
      <view v-else-if="errorMessage" class="status-message error">{{errorMessage}}<button @click="loadPackages">重新加载</button></view>
      <view v-else-if="!packages.length" class="loading-panel"><PackageOpen :size="32"/><text>暂时没有可购买的套餐</text></view>
      <view v-else class="package-grid">
        <view v-for="(item,index) in packages" :key="item.id" class="package-card" :class="{featured:index===1}">
          <view class="package-top"><text class="package-name">{{item.name}}</text><text v-if="index===1" class="recommended">推荐</text></view>
          <view class="credit-count"><text>{{item.credit_count}}</text><text>次起名额度</text></view>
          <view class="price"><text>¥</text><text>{{formatPrice(item.price)}}</text></view>
          <view class="package-points"><view><Check :size="16"/><text>购买后立即到账</text></view><view><Check :size="16"/><text>用于首次起名和反馈调整</text></view></view>
          <button class="buy-button" :disabled="payingId===item.id" @click="selectPackage(item)"><LoaderCircle v-if="payingId===item.id" class="spin" :size="18"/><ShoppingBag v-else :size="18"/><text>{{payingId===item.id?'正在创建订单…':'选择套餐'}}</text></button>
        </view>
      </view>
      <view class="pay-notice"><ShieldCheck :size="19"/><view><text>支付宝网页支付</text><text>确认购买后会离开当前页面并跳转到支付宝。支付结果和额度增加由后端处理。</text></view></view>
    </view>
  </view>
</template>

<script setup>
import {ref} from 'vue'; import {onLoad} from '@dcloudio/uni-app'; import {ArrowLeft,LoaderCircle,PackageOpen,Check,ShoppingBag,ShieldCheck} from '@lucide/vue'; import {packageApi} from '../../api'; import {useAuthStore} from '../../stores/auth'; import {requireAuth} from '../../utils/storage'
const authStore=useAuthStore(); const packages=ref([]); const loading=ref(true); const errorMessage=ref(''); const payingId=ref(null)
onLoad(async()=>{if(!requireAuth())return;try{await authStore.refreshBalance()}catch(_){}await loadPackages()})
function goBack(){const pages=getCurrentPages();if(pages.length>1)uni.navigateBack();else uni.redirectTo({url:'/pages/profile/profile'})}
function formatPrice(value){const number=Number(value);return Number.isFinite(number)?number.toFixed(2):value}
async function loadPackages(){loading.value=true;errorMessage.value='';try{packages.value=await packageApi.list()}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
async function selectPackage(item){payingId.value=item.id;errorMessage.value='';try{const detail=await packageApi.detail(item.id);uni.showModal({title:`购买 ${detail.name}`,content:`支付 ¥${formatPrice(detail.price)}，获得 ${detail.credit_count} 次起名额度。确认后将跳转支付宝。`,confirmText:'确认购买',success:async({confirm})=>{if(!confirm){payingId.value=null;return}try{const order=await packageApi.createOrder(detail.id);
  // #ifdef H5
  window.location.assign(order.pay_url)
  // #endif
  // #ifndef H5
  plus.runtime.openURL(order.pay_url)
  // #endif
}catch(error){errorMessage.value=error.message;payingId.value=null}}})}catch(error){errorMessage.value=error.message;payingId.value=null}}
</script>

<style scoped>
.packages-page{padding-bottom:70rpx}.packages-header{display:grid;grid-template-columns:76rpx minmax(0,1fr) auto;align-items:center;gap:22rpx;margin-bottom:42rpx}.back-button{display:flex;width:72rpx;height:72rpx;align-items:center;justify-content:center;border:1px solid #d1dad6;border-radius:6px;background:#fff;color:#38463f}.current-balance{text-align:right}.current-balance text:first-child{display:block;color:#7d8782;font-size:21rpx}.current-balance text:last-child{display:block;margin-top:4rpx;color:#176c57;font-size:27rpx;font-weight:700}.package-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20rpx}.package-card{display:flex;min-height:550rpx;flex-direction:column;border:1px solid #dce2df;border-radius:8px;background:#fff;padding:30rpx}.package-card.featured{border:2rpx solid #16836b}.package-top{display:flex;min-height:50rpx;align-items:center;justify-content:space-between;gap:12rpx}.package-name{font-size:29rpx;font-weight:750}.recommended{border-radius:4px;background:#eaf4f0;padding:7rpx 11rpx;color:#126e58;font-size:20rpx}.credit-count{margin-top:32rpx}.credit-count text:first-child{display:block;font-size:58rpx;font-weight:760;line-height:1.15}.credit-count text:last-child{display:block;margin-top:7rpx;color:#727d77;font-size:23rpx}.price{display:flex;align-items:baseline;margin-top:28rpx;color:#c04b3f}.price text:first-child{font-size:25rpx}.price text:last-child{font-size:45rpx;font-weight:760}.package-points{margin-top:28rpx;color:#5e6963;font-size:22rpx}.package-points view{display:flex;align-items:flex-start;gap:9rpx;margin-top:13rpx}.package-points svg{flex:0 0 auto;color:#16836b}.buy-button{display:flex;width:100%;min-height:80rpx;align-items:center;justify-content:center;gap:10rpx;margin-top:auto;border-radius:6px;background:#263c34;color:#fff;font-size:25rpx}.featured .buy-button{background:#167861}.loading-panel{display:flex;min-height:380rpx;flex-direction:column;align-items:center;justify-content:center;gap:20rpx;color:#67736d}.status-message button{margin-top:16rpx;background:transparent;color:#9d3b31;font-size:24rpx;text-decoration:underline}.pay-notice{display:flex;max-width:760rpx;align-items:flex-start;gap:14rpx;margin:36rpx auto 0;color:#6e7873}.pay-notice svg{flex:0 0 auto;color:#16836b}.pay-notice text:first-child{display:block;color:#3c4842;font-size:24rpx;font-weight:650}.pay-notice text:last-child{display:block;margin-top:5rpx;font-size:21rpx;line-height:1.6}.spin{animation:spin .85s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}@media(max-width:760px){.packages-header{grid-template-columns:64rpx minmax(0,1fr)}.current-balance{display:none}.package-grid{grid-template-columns:1fr}.package-card{min-height:440rpx}.credit-count{margin-top:22rpx}}
</style>
