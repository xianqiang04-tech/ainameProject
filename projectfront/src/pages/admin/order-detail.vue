<template>
  <AdminShell active="orders" title="订单详情" subtitle="核对订单、用户与支付信息">
    <template #actions><button class="admin-button" @click="back"><ArrowLeft :size="16"/><text>返回订单列表</text></button></template>
    <view v-if="loading" class="admin-data-panel"><view class="admin-state"><LoaderCircle class="admin-spin" :size="26"/><strong>正在读取订单详情</strong></view></view>
    <view v-else-if="errorMessage" class="admin-data-panel"><view class="admin-state"><AlertCircle :size="28"/><strong>订单详情加载失败</strong><text>{{errorMessage}}</text><button class="admin-button" @click="loadOrder">重新加载</button></view></view>
    <view v-else-if="order" class="order-detail">
      <view class="order-heading"><view class="order-icon"><ReceiptText :size="25"/></view><view><text>{{order.order_no}}</text><text>订单 ID {{order.id}}</text></view><StatusBadge type="order" :value="order.status"/></view>
      <view class="admin-detail-band">
        <view class="admin-detail-section"><text class="admin-detail-title">订单信息</text><view class="admin-detail-grid"><view class="admin-detail-item"><text>订单金额</text><text class="amount">{{formatMoney(order.amount)}}</text></view><view class="admin-detail-item"><text>包含次数</text><text>{{order.credit_count}} 次</text></view><view class="admin-detail-item"><text>套餐</text><text>{{order.package_name}}（ID {{order.package_id}}）</text></view><view class="admin-detail-item"><text>创建时间</text><text>{{formatDateTime(order.created_at)}}</text></view><view class="admin-detail-item"><text>支付时间</text><text>{{formatDateTime(order.paid_at)}}</text></view><view class="admin-detail-item"><text>支付宝交易号</text><text>{{order.alipay_trade_no||'--'}}</text></view></view></view>
        <view class="admin-detail-section"><text class="admin-detail-title">下单用户</text><view class="admin-detail-grid"><view class="admin-detail-item"><text>用户名</text><text>{{order.username}}</text></view><view class="admin-detail-item"><text>邮箱</text><text>{{order.user_email}}</text></view><view class="admin-detail-item"><text>用户 ID</text><text>{{order.user_id}}</text></view></view></view>
      </view>
      <view class="read-only-note"><LockKeyhole :size="17"/><text>订单信息为只读，管理后台不能修改支付状态或交易结果。</text></view>
    </view>
  </AdminShell>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { AlertCircle, ArrowLeft, LoaderCircle, LockKeyhole, ReceiptText } from '@lucide/vue'
import AdminShell from '../../components/admin/AdminShell.vue';import StatusBadge from '../../components/admin/StatusBadge.vue';import { adminApi } from '../../api';import { useAdminStore } from '../../stores/admin';import { formatDateTime,formatMoney,requireAdminPage } from '../../utils/admin'
const adminStore=useAdminStore();const orderId=ref(null);const order=ref(null);const loading=ref(true);const errorMessage=ref('')
onLoad(({orderId:id})=>{orderId.value=Number(id)||null});onShow(async()=>{if(await requireAdminPage(adminStore)&&orderId.value)await loadOrder()})
async function loadOrder(){loading.value=true;errorMessage.value='';try{order.value=await adminApi.orderDetail(orderId.value)}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function back(){uni.navigateBack({fail:()=>uni.redirectTo({url:'/pages/admin/orders'})})}
</script>

<style scoped>
.order-detail{max-width:980px}.order-heading{display:flex;align-items:center;gap:14px;margin-bottom:16px;border:1px solid #dfe5e2;border-radius:8px;background:#fff;padding:19px}.order-icon{display:flex;width:46px;height:46px;flex:0 0 auto;align-items:center;justify-content:center;border-radius:7px;background:#e8f3ef;color:#176f59}.order-heading>view:nth-child(2){min-width:0;flex:1}.order-heading>view:nth-child(2) text:first-child{display:block;overflow:hidden;color:#202a25;font-size:16px;font-weight:730;text-overflow:ellipsis;white-space:nowrap}.order-heading>view:nth-child(2) text:last-child{display:block;margin-top:5px;color:#7b8781;font-size:11px}.amount{color:#176f59!important;font-size:18px!important;font-weight:750}.read-only-note{display:flex;align-items:center;gap:9px;margin-top:14px;border:1px solid #dce3df;border-radius:7px;background:#f8faf9;padding:13px 15px;color:#6f7c76;font-size:12px}@media(max-width:480px){.order-heading{align-items:flex-start}.order-heading>text:last-child{flex:0 0 auto}}
</style>
