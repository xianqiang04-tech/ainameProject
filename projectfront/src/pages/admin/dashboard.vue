<template>
  <AdminShell active="dashboard" title="概览" subtitle="查看当前用户、订单与收入概况">
    <template #actions><button class="admin-button" :disabled="loading" @click="loadDashboard"><RefreshCw :class="{ 'admin-spin': loading }" :size="16"/><text>刷新</text></button></template>
    <view v-if="errorMessage" class="dashboard-error"><AlertCircle :size="18"/><view><text>概览加载失败</text><text>{{ errorMessage }}</text></view><button @click="loadDashboard">重试</button></view>
    <view v-else class="metrics-grid">
      <view v-for="item in metrics" :key="item.key" class="metric-item">
        <view class="metric-icon" :class="item.tone"><component :is="item.icon" :size="21"/></view>
        <view><text>{{ item.label }}</text><text>{{ loading ? '--' : item.value }}</text><text>{{ item.note }}</text></view>
      </view>
    </view>
    <view class="module-band">
      <view class="module-heading"><text>管理模块</text><text>选择一个模块开始处理</text></view>
      <view class="module-grid">
        <button v-for="item in modules" :key="item.url" @click="go(item.url)"><view><component :is="item.icon" :size="21"/></view><text>{{ item.label }}</text><text>{{ item.note }}</text><ArrowUpRight :size="17"/></button>
      </view>
    </view>
  </AdminShell>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { AlertCircle, ArrowUpRight, BadgeDollarSign, CheckCircle2, ClipboardList, Package, RefreshCw, ScrollText, UserCheck, Users } from '@lucide/vue'
import AdminShell from '../../components/admin/AdminShell.vue'
import { adminApi } from '../../api'
import { useAdminStore } from '../../stores/admin'
import { formatMoney, requireAdminPage } from '../../utils/admin'

const adminStore = useAdminStore()
const loading = ref(true)
const errorMessage = ref('')
const data = ref({ user_count:0, active_user_count:0, order_count:0, paid_order_count:0, paid_revenue:0 })
const metrics = computed(() => [
  {key:'users',label:'用户总数',value:data.value.user_count,note:'全部注册账号',icon:Users,tone:'green'},
  {key:'active',label:'有效用户',value:data.value.active_user_count,note:'当前可登录账号',icon:UserCheck,tone:'teal'},
  {key:'orders',label:'订单总数',value:data.value.order_count,note:'全部订单记录',icon:ClipboardList,tone:'ink'},
  {key:'paid',label:'已支付订单',value:data.value.paid_order_count,note:'支付状态为已完成',icon:CheckCircle2,tone:'green'},
  {key:'revenue',label:'已支付金额',value:formatMoney(data.value.paid_revenue),note:'按已支付订单统计',icon:BadgeDollarSign,tone:'red'},
])
const modules = [
  {label:'用户管理',note:'账号、状态与次数',icon:Users,url:'/pages/admin/users'},
  {label:'套餐管理',note:'价格、次数与启停',icon:Package,url:'/pages/admin/packages'},
  {label:'订单查询',note:'订单与支付信息',icon:ClipboardList,url:'/pages/admin/orders'},
  {label:'审计日志',note:'管理员操作记录',icon:ScrollText,url:'/pages/admin/audit'},
]

onShow(async()=>{ if(await requireAdminPage(adminStore)) await loadDashboard() })
async function loadDashboard(){loading.value=true;errorMessage.value='';try{data.value=await adminApi.dashboard()}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function go(url){uni.redirectTo({url})}
</script>

<style scoped>
.metrics-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}.metric-item{display:flex;min-width:0;gap:13px;border:1px solid #dfe5e2;border-radius:8px;background:#fff;padding:19px}.metric-icon{display:flex;width:38px;height:38px;flex:0 0 auto;align-items:center;justify-content:center;border-radius:7px}.metric-icon.green{background:#e8f4ef;color:#176f59}.metric-icon.teal{background:#e7f3f3;color:#28706e}.metric-icon.ink{background:#edf0ef;color:#394942}.metric-icon.red{background:#fff0ed;color:#ad493d}.metric-item>view:last-child{min-width:0}.metric-item text:first-child{display:block;color:#728079;font-size:11px}.metric-item text:nth-child(2){display:block;overflow:hidden;margin-top:7px;color:#1d2722;font-size:24px;font-weight:750;text-overflow:ellipsis;white-space:nowrap}.metric-item text:last-child{display:block;overflow:hidden;margin-top:4px;color:#939d98;font-size:10px;text-overflow:ellipsis;white-space:nowrap}.module-band{margin-top:24px}.module-heading text:first-child{display:block;color:#26312c;font-size:15px;font-weight:700}.module-heading text:last-child{display:block;margin-top:4px;color:#839089;font-size:11px}.module-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:14px}.module-grid button{position:relative;display:grid;min-height:130px;grid-template-columns:42px 1fr;grid-template-rows:auto auto;align-content:center;gap:4px 12px;border:1px solid #e0e6e3;border-radius:7px;background:#fff;padding:18px;color:#33413b;text-align:left}.module-grid button>view{display:flex;width:42px;height:42px;grid-row:1/3;align-items:center;justify-content:center;border-radius:7px;background:#e8f3ef;color:#176f59}.module-grid button>text:nth-child(2){align-self:end;font-size:14px;font-weight:700}.module-grid button>text:nth-child(3){align-self:start;color:#7c8882;font-size:11px}.module-grid button>svg{position:absolute;top:13px;right:13px;color:#9ba59f}.dashboard-error{display:flex;align-items:center;gap:13px;border:1px solid #e8c2bd;border-radius:8px;background:#fff5f3;padding:18px;color:#a44438}.dashboard-error view{flex:1}.dashboard-error view text:first-child{display:block;font-size:14px;font-weight:700}.dashboard-error view text:last-child{display:block;margin-top:4px;font-size:11px}.dashboard-error button{height:34px;border:1px solid #dfaea7;border-radius:6px;background:#fff;color:#a44438;padding:0 13px;font-size:12px}@media(max-width:1180px){.metrics-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:760px){.metrics-grid{grid-template-columns:1fr 1fr}.module-grid{grid-template-columns:1fr 1fr}.module-grid button{min-height:112px}}@media(max-width:420px){.metrics-grid,.module-grid{grid-template-columns:1fr}.metric-item{padding:16px}}
</style>
