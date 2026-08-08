<template>
  <view class="page-shell">
    <BrandHeader />
    <view class="page-content logo-layout">
      <view class="panel logo-form">
        <view class="page-heading"><view><text class="section-title">企业 Logo 生成</text><text class="section-note">输入企业名和希望呈现的气质，生成一版可预览的 Logo。</text></view><Palette :size="30" /></view>
        <view class="form-group"><text class="field-label">企业名称</text><input v-model.trim="companyName" class="input-control" maxlength="40" placeholder="例如：远川科技" /></view>
        <view class="form-group"><text class="field-label">风格要求（选填）</text><textarea v-model="styleFeedback" class="textarea-control" maxlength="300" placeholder="例如：简洁、可靠，适合科技服务行业，避免复杂图形…" /></view>
        <button class="primary-button generate-button" :disabled="loading" @click="generate"><LoaderCircle v-if="loading" class="spin" :size="20" /><Paintbrush v-else :size="20" /><text>{{loading?'正在生成，可能需要几分钟…':'生成 Logo'}}</text></button>
        <view v-if="authStore.logoBalance!==null" class="balance-note"><text>剩余 Logo 次数：{{authStore.logoBalance}}</text><text class="balance-link" @click="goPackages">购买次数包</text></view>
        <view v-if="errorMessage" class="status-message error">{{errorMessage}}</view>
      </view>
      <view class="preview-area">
        <view v-if="loading" class="preview-empty panel"><LoaderCircle class="spin preview-loader" :size="38"/><text>正在完成视觉方案</text><text class="section-note">请保持页面打开，生成完成后会自动显示。</text></view>
        <view v-else-if="!result" class="preview-empty panel"><view class="preview-placeholder"><Shapes :size="36"/></view><text>Logo 预览区</text><text class="section-note">生成后的图片和提示词会显示在这里。</text></view>
        <view v-else class="result-wrap">
          <view class="logo-canvas"><image class="logo-image" :src="logoUrl" mode="aspectFit" @click="previewImage" /></view>
          <view class="result-meta panel"><view class="result-title"><view><text>{{result.company_name}}</text><text>{{result.logo_status}}</text></view><button class="icon-button" title="预览原图" @click="previewImage"><Maximize2 :size="19"/></button></view><text class="prompt-label">生成提示词</text><text class="prompt-text">{{result.logo_prompt}}</text><button class="secondary-button download-button" @click="downloadImage"><Download :size="18"/><text>下载图片</text></button></view>
        </view>
      </view>
    </view>
    <BottomNav active="logo" />
  </view>
</template>

<script setup>
import { computed,ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { Palette,Paintbrush,LoaderCircle,Shapes,Maximize2,Download } from '@lucide/vue'
import BrandHeader from '../../components/BrandHeader.vue'; import BottomNav from '../../components/BottomNav.vue'
import { logoApi } from '../../api'; import { resolveAssetUrl } from '../../config'; import { useAuthStore } from '../../stores/auth'; import { requireAuth } from '../../utils/storage'
const authStore=useAuthStore(); const companyName=ref(''); const styleFeedback=ref(''); const loading=ref(false); const errorMessage=ref(''); const result=ref(null); const logoUrl=computed(()=>resolveAssetUrl(result.value?.logo_url))
onShow(async()=>{if(!requireAuth())return;try{await authStore.refreshBalance()}catch(_){}})
function goPackages(){uni.navigateTo({url:'/pages/packages/packages?tab=logo'})}
async function generate(){if(!companyName.value)return uni.showToast({title:'请先输入企业名称',icon:'none'});if(authStore.logoBalance===0){uni.showModal({title:'Logo 次数不足',content:'前往套餐页购买 Logo 次数包后再继续。',confirmText:'查看套餐',success:({confirm})=>{if(confirm)uni.navigateTo({url:'/pages/packages/packages?tab=logo'})}});return}loading.value=true;errorMessage.value='';try{result.value=await logoApi.generate({company_name:companyName.value,style_feedback:styleFeedback.value});await authStore.refreshBalance()}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function previewImage(){if(logoUrl.value)uni.previewImage({urls:[logoUrl.value],current:logoUrl.value})}
function downloadImage(){if(!logoUrl.value)return;
  // #ifdef H5
  const link=document.createElement('a');link.href=logoUrl.value;link.download=`${result.value.company_name}-logo.png`;link.target='_blank';document.body.appendChild(link);link.click();link.remove()
  // #endif
  // #ifndef H5
  uni.downloadFile({url:logoUrl.value,success:({tempFilePath})=>uni.saveImageToPhotosAlbum({filePath:tempFilePath})})
  // #endif
}
</script>

<style scoped>
.logo-layout{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:28rpx;align-items:start}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:20rpx}.page-heading svg{color:#c75649}.generate-button{width:100%;margin-top:34rpx}.spin{animation:spin .85s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.preview-empty{display:flex;min-height:620rpx;flex-direction:column;align-items:center;justify-content:center;text-align:center}.preview-empty>text:first-of-type{display:block;margin-bottom:10rpx;color:#2b3530;font-size:30rpx;font-weight:700}.preview-loader{margin-bottom:22rpx;color:#16836b}.preview-placeholder{display:flex;width:96rpx;height:96rpx;align-items:center;justify-content:center;margin-bottom:24rpx;border-radius:8px;background:#eef2f0;color:#6d7973}.logo-canvas{display:flex;aspect-ratio:1/1;align-items:center;justify-content:center;overflow:hidden;border:1px solid #dce2df;border-radius:8px;background:#fff}.balance-note{display:flex;align-items:center;justify-content:space-between;margin-top:18rpx;color:#77817c;font-size:23rpx}.balance-link{color:#16836b;font-weight:600}.logo-image{width:100%;height:100%}.result-meta{margin-top:18rpx}.result-title{display:flex;align-items:flex-start;justify-content:space-between;gap:20rpx}.result-title view text:first-child{display:block;font-size:32rpx;font-weight:750}.result-title view text:last-child{display:block;margin-top:7rpx;color:#16836b;font-size:23rpx}.icon-button{display:flex;width:68rpx;height:68rpx;align-items:center;justify-content:center;border:1px solid #d0d9d5;border-radius:6px;background:#fff;color:#486158}.prompt-label{display:block;margin-top:28rpx;color:#77817c;font-size:22rpx}.prompt-text{display:block;margin-top:8rpx;color:#3a4640;font-size:24rpx;line-height:1.7}.download-button{width:100%;margin-top:26rpx}@media(max-width:820px){.logo-layout{display:block}.preview-area{margin-top:28rpx}.preview-empty{min-height:400rpx}.result-wrap{max-width:720rpx;margin:0 auto}}
</style>
