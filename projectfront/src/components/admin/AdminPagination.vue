<template>
  <view v-if="total > 0" class="pagination">
    <text>共 {{ total }} 条</text>
    <view>
      <button :disabled="loading || page <= 1" aria-label="上一页" @click="$emit('change', page - 1)"><ChevronLeft :size="17" /></button>
      <text>{{ page }} / {{ totalPages }}</text>
      <button :disabled="loading || page >= totalPages" aria-label="下一页" @click="$emit('change', page + 1)"><ChevronRight :size="17" /></button>
    </view>
  </view>
</template>
<script setup>
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from '@lucide/vue'
const props = defineProps({ page:{type:Number,required:true}, pageSize:{type:Number,required:true}, total:{type:Number,required:true}, loading:Boolean })
defineEmits(['change'])
const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
</script>
<style scoped>
.pagination{display:flex;align-items:center;justify-content:space-between;gap:16px;border-top:1px solid #e8ecea;padding:16px 18px;color:#74807a;font-size:13px}.pagination>view{display:flex;align-items:center;gap:10px}.pagination button{display:flex;width:34px;height:34px;align-items:center;justify-content:center;border:1px solid #d5deda;border-radius:6px;background:#fff;color:#33423c}.pagination button[disabled]{background:#f4f6f5;color:#b7bfbb}.pagination view text{min-width:58px;color:#53615b;text-align:center}@media(max-width:480px){.pagination{padding:14px}.pagination>text{font-size:12px}}
</style>
