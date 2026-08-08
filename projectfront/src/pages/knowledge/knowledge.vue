<template>
  <view class="page-shell">
    <BrandHeader />
    <view class="page-content knowledge-layout">
      <view class="page-heading">
        <view><text class="section-title">专属知识库</text><text class="section-note">上传你的命名规则、品牌背景或偏好资料，后续起名会参考这些内容。</text></view>
        <Database :size="32" :stroke-width="1.5" />
      </view>
      <view class="upload-panel panel">
        <button class="drop-zone" :disabled="uploading" @click="chooseFile">
          <view class="upload-icon"><FileUp :size="32" :stroke-width="1.6" /></view>
          <template v-if="selectedFile">
            <text class="drop-title">{{ selectedFile.name }}</text>
            <text class="drop-note">{{ formatSize(selectedFile.size) }} · 点击重新选择</text>
          </template>
          <template v-else>
            <text class="drop-title">选择 TXT 或 PDF 文件</text>
            <text class="drop-note">单次上传一个文件，选择后再确认提交</text>
          </template>
        </button>
        <view class="file-rules">
          <view><FileText :size="18" /><text>TXT 文本资料</text></view>
          <view><FileType2 :size="18" /><text>PDF 文档</text></view>
          <view><ShieldCheck :size="18" /><text>仅用于你的专属知识库</text></view>
        </view>
        <button class="primary-button upload-button" :disabled="!selectedFile || uploading" @click="upload">
          <LoaderCircle v-if="uploading" class="spin" :size="20" /><UploadCloud v-else :size="20" />
          <text>{{ uploading ? '正在上传…' : '提交到知识库' }}</text>
        </button>
        <view v-if="statusMessage" class="status-message" :class="{ error: statusType === 'error' }">{{ statusMessage }}</view>
      </view>
      <view class="process-row">
        <view><text class="step-number">1</text><text>选择资料</text></view><ChevronRight :size="18" />
        <view><text class="step-number">2</text><text>提交处理</text></view><ChevronRight :size="18" />
        <view><text class="step-number">3</text><text>起名时引用</text></view>
      </view>
      <view class="notice"><Info :size="18" /><text>后端暂未提供处理进度查询。页面显示“已提交”表示文件已进入处理队列，不代表知识库已经构建完成。</text></view>
    </view>
    <BottomNav active="knowledge" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { Database, FileUp, FileText, FileType2, ShieldCheck, UploadCloud, LoaderCircle, ChevronRight, Info } from '@lucide/vue'
import BrandHeader from '../../components/BrandHeader.vue'
import BottomNav from '../../components/BottomNav.vue'
import { knowledgeApi } from '../../api'
import { useAuthStore } from '../../stores/auth'
import { requireAuth } from '../../utils/storage'

const authStore=useAuthStore(); const selectedFile=ref(null); const uploading=ref(false); const statusMessage=ref(''); const statusType=ref('success')
onShow(async()=>{ if(!requireAuth()) return; try{await authStore.refreshBalance()}catch(_){} })
function formatSize(size=0){ if(size<1024) return `${size} B`; if(size<1024*1024) return `${(size/1024).toFixed(1)} KB`; return `${(size/1024/1024).toFixed(1)} MB` }
function chooseFile(){
  uni.chooseFile({ count:1, extension:['.txt','.pdf'], success:(res)=>{ const file=res.tempFiles?.[0]; if(!file) return; const ext=file.name.split('.').pop().toLowerCase(); if(!['txt','pdf'].includes(ext)) return uni.showToast({title:'只支持 TXT 或 PDF',icon:'none'}); selectedFile.value=file; statusMessage.value='' }, fail:(error)=>{ if(!error.errMsg?.includes('cancel')) { statusType.value='error'; statusMessage.value='无法选择文件，请使用 H5 浏览器重试' } } })
}
async function upload(){ if(!selectedFile.value) return; uploading.value=true; statusMessage.value=''; try{ const data=await knowledgeApi.upload(selectedFile.value.path); statusType.value='success'; statusMessage.value=data.message||'文件已提交，后台正在构建知识库'; selectedFile.value=null }catch(error){statusType.value='error';statusMessage.value=error.message}finally{uploading.value=false} }
</script>

<style scoped>
.knowledge-layout{max-width:900rpx}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:24rpx;margin-bottom:28rpx}.page-heading svg{color:#16836b}.upload-panel{padding:36rpx}.drop-zone{display:flex;width:100%;min-height:360rpx;flex-direction:column;align-items:center;justify-content:center;border:2rpx dashed #b7c8c1;border-radius:8px;background:#f8fbfa;padding:34rpx;color:#42514b}.upload-icon{display:flex;width:92rpx;height:92rpx;align-items:center;justify-content:center;margin-bottom:24rpx;border-radius:8px;background:#e6f2ed;color:#16725c}.drop-title{display:block;max-width:100%;overflow:hidden;color:#23302a;font-size:30rpx;font-weight:700;text-overflow:ellipsis;white-space:nowrap}.drop-note{display:block;margin-top:10rpx;color:#7a8580;font-size:24rpx}.file-rules{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16rpx;margin-top:24rpx}.file-rules view{display:flex;min-height:68rpx;align-items:center;justify-content:center;gap:10rpx;border-radius:6px;background:#f2f5f3;color:#58645e;font-size:23rpx}.upload-button{width:100%;margin-top:28rpx}.spin{animation:spin .85s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.process-row{display:flex;align-items:center;justify-content:center;gap:18rpx;margin:30rpx 0;color:#77817c;font-size:23rpx}.process-row>view{display:flex;align-items:center;gap:9rpx}.step-number{display:flex;width:38rpx;height:38rpx;align-items:center;justify-content:center;border:1px solid #c8d3ce;border-radius:50%;background:#fff;color:#236653;font-size:20rpx}.notice{display:flex;align-items:flex-start;gap:12rpx;border-left:5rpx solid #d4a13f;background:#fff9ed;padding:20rpx 22rpx;color:#715b31;font-size:23rpx;line-height:1.65}.notice svg{flex:0 0 auto;margin-top:4rpx}@media(max-width:600px){.file-rules{grid-template-columns:1fr}.process-row{gap:8rpx}.process-row>svg{display:none}.process-row>view{flex:1;flex-direction:column;text-align:center}.drop-zone{min-height:300rpx}}
.knowledge-layout { max-width: 900px; }
</style>
