<template>
  <view v-if="open" class="modal-layer" @click.self="$emit('close')">
    <view class="modal-panel" :style="{ maxWidth: width }">
      <view class="modal-header"><view><text>{{ title }}</text><text v-if="subtitle">{{ subtitle }}</text></view><button aria-label="关闭" @click="$emit('close')"><X :size="20" /></button></view>
      <view class="modal-body"><slot /></view>
      <view class="modal-footer"><slot name="footer" /></view>
    </view>
  </view>
</template>
<script setup>
import { X } from '@lucide/vue'
defineProps({ open:Boolean, title:{type:String,required:true}, subtitle:{type:String,default:''}, width:{type:String,default:'520px'} })
defineEmits(['close'])
</script>
<style scoped>
.modal-layer{position:fixed;z-index:100;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(20,29,25,.48);padding:24px}.modal-panel{overflow:hidden;width:100%;max-height:calc(100vh - 48px);border:1px solid #d8dfdc;border-radius:8px;background:#fff;box-shadow:0 24px 60px rgba(17,31,25,.22)}.modal-header{display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #e5e9e7;padding:20px 22px}.modal-header view{min-width:0}.modal-header view text:first-child{display:block;color:#1c2521;font-size:18px;font-weight:700}.modal-header view text:last-child{display:block;margin-top:4px;color:#79847e;font-size:12px}.modal-header button{display:flex;width:34px;height:34px;align-items:center;justify-content:center;border-radius:6px;background:#f3f5f4;color:#54625c}.modal-body{overflow-y:auto;max-height:calc(100vh - 190px);padding:22px}.modal-footer{display:flex;align-items:center;justify-content:flex-end;gap:10px;border-top:1px solid #e5e9e7;padding:16px 22px}@media(max-width:560px){.modal-layer{align-items:flex-end;padding:0}.modal-panel{max-width:none!important;max-height:92vh;border-right:0;border-bottom:0;border-left:0;border-radius:8px 8px 0 0}.modal-body{max-height:calc(92vh - 142px)}}
</style>
