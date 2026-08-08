<template>
  <view class="nav-wrap"><view class="bottom-nav">
    <button v-for="item in items" :key="item.key" class="nav-item" :class="{ active: active === item.key }" @click="go(item)">
      <component :is="item.icon" :size="21" :stroke-width="active === item.key ? 2.2 : 1.7" /><text>{{ item.label }}</text>
    </button>
  </view></view>
</template>
<script setup>
import { WandSparkles, LibraryBig, Palette, UserRound } from '@lucide/vue'
const props = defineProps({ active: { type: String, required: true } })
const items = [
  { key:'naming', label:'起名', icon:WandSparkles, url:'/pages/naming/naming' },
  { key:'knowledge', label:'知识库', icon:LibraryBig, url:'/pages/knowledge/knowledge' },
  { key:'logo', label:'Logo', icon:Palette, url:'/pages/logo/logo' },
  { key:'profile', label:'我的', icon:UserRound, url:'/pages/profile/profile' },
]
function go(item) { if (item.key !== props.active) uni.redirectTo({ url:item.url }) }
</script>
<style scoped>
.nav-wrap { position:fixed; z-index:30; right:0; bottom:0; left:0; padding:0 24rpx calc(18rpx + env(safe-area-inset-bottom)); pointer-events:none; }
.bottom-nav { display:grid; width:100%; max-width:780rpx; grid-template-columns:repeat(4,minmax(0,1fr)); margin:0 auto; border:1px solid #dce2df; border-radius:8px; background:rgba(255,255,255,.97); padding:10rpx; box-shadow:0 10px 30px rgba(25,47,39,.13); pointer-events:auto; }
.nav-item { display:flex; min-width:0; min-height:76rpx; flex-direction:column; align-items:center; justify-content:center; gap:4rpx; border-radius:6px; background:transparent; color:#77817c; font-size:21rpx; line-height:1; }
.nav-item.active { background:#eaf4f0; color:#126e58; }
</style>
