<template><text class="status-badge" :class="tone">{{ label }}</text></template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ type:{type:String,required:true}, value:{type:[String,Boolean],required:true} })
const state = computed(() => {
  if (props.type === 'active') return props.value ? {label:'正常',tone:'success'} : {label:'已停用',tone:'danger'}
  if (props.type === 'package') return props.value ? {label:'已启用',tone:'success'} : {label:'已停用',tone:'neutral'}
  if (props.type === 'order') return props.value === 'paid' ? {label:'已支付',tone:'success'} : {label:'待支付',tone:'warning'}
  return { label:String(props.value), tone:'neutral' }
})
const label = computed(() => state.value.label)
const tone = computed(() => state.value.tone)
</script>
<style scoped>
.status-badge{display:inline-flex;height:24px;align-items:center;border:1px solid transparent;border-radius:5px;padding:0 8px;font-size:12px;font-weight:650;line-height:1}.success{border-color:#b8d9cc;background:#edf7f3;color:#176b57}.danger{border-color:#e7c0bb;background:#fff2f0;color:#a84236}.warning{border-color:#ead6a7;background:#fff9e9;color:#8a6720}.neutral{border-color:#d8dfdc;background:#f3f5f4;color:#65716b}
</style>
