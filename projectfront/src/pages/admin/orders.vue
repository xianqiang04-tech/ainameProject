<template>
  <AdminShell active="orders" title="订单查询" subtitle="查看订单金额、套餐与支付状态">
    <template #actions><button class="admin-button" :disabled="loading" @click="loadOrders"><RefreshCw :class="{'admin-spin':loading}" :size="16"/><text>刷新</text></button></template>
    <view class="admin-filter-panel order-filters">
      <view class="admin-filter-field grow"><text class="admin-filter-label">订单号</text><input v-model.trim="filters.order_no" class="admin-input" placeholder="输入完整或部分订单号" @confirm="search"/></view>
      <view class="admin-filter-field"><text class="admin-filter-label">用户 ID</text><input v-model.trim="filters.user_id" class="admin-input" type="number" placeholder="全部用户" @confirm="search"/></view>
      <view class="admin-filter-field"><text class="admin-filter-label">支付状态</text><picker :range="statusOptions" range-key="label" :value="statusIndex" @change="changeStatus"><view class="admin-select"><text>{{statusOptions[statusIndex].label}}</text><ChevronDown :size="15"/></view></picker></view>
      <button class="admin-button primary" :disabled="loading" @click="search"><Search :size="16"/><text>查询</text></button><button class="admin-button" :disabled="loading" @click="reset"><RotateCcw :size="16"/><text>重置</text></button>
    </view>
    <view class="admin-data-panel">
      <view v-if="loading" class="admin-state"><LoaderCircle class="admin-spin" :size="26"/><strong>正在读取订单</strong></view>
      <view v-else-if="errorMessage" class="admin-state"><AlertCircle :size="28"/><strong>订单列表加载失败</strong><text>{{errorMessage}}</text><button class="admin-button" @click="loadOrders">重新加载</button></view>
      <view v-else-if="!result.items.length" class="admin-state"><ClipboardList :size="30"/><strong>没有匹配的订单</strong><text>调整订单号、用户或状态筛选后再试。</text></view>
      <view v-else class="admin-table-scroll"><view class="admin-table orders-table">
        <view class="admin-table-row header"><view class="admin-table-cell">订单</view><view class="admin-table-cell">用户</view><view class="admin-table-cell">套餐</view><view class="admin-table-cell">金额</view><view class="admin-table-cell">状态</view><view class="admin-table-cell">创建时间</view><view class="admin-table-cell"></view></view>
        <view v-for="item in result.items" :key="item.id" class="admin-table-row"><view class="admin-table-cell" data-label="订单"><view><strong>{{item.order_no}}</strong><small>ID {{item.id}}</small></view></view><view class="admin-table-cell" data-label="用户"><view><strong>{{item.username}}</strong><small>{{item.user_email}} · ID {{item.user_id}}</small></view></view><view class="admin-table-cell" data-label="套餐"><view><strong>{{item.package_name}}</strong><small>{{item.credit_count}} 次</small></view></view><view class="admin-table-cell" data-label="金额"><strong>{{formatMoney(item.amount)}}</strong></view><view class="admin-table-cell" data-label="状态"><StatusBadge type="order" :value="item.status"/></view><view class="admin-table-cell" data-label="创建时间"><text>{{formatDateTime(item.created_at)}}</text></view><view class="admin-table-cell admin-table-actions" data-label="操作"><button class="admin-link-button" @click="openDetail(item.id)"><Eye :size="15"/><text>详情</text></button></view></view>
      </view></view>
      <AdminPagination :page="result.page" :page-size="result.page_size" :total="result.total" :loading="loading" @change="changePage"/>
    </view>
  </AdminShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { AlertCircle, ChevronDown, ClipboardList, Eye, LoaderCircle, RefreshCw, RotateCcw, Search } from '@lucide/vue'
import AdminPagination from '../../components/admin/AdminPagination.vue';import AdminShell from '../../components/admin/AdminShell.vue';import StatusBadge from '../../components/admin/StatusBadge.vue'
import { adminApi } from '../../api';import { useAdminStore } from '../../stores/admin';import { formatDateTime,formatMoney,normalizeInteger,requireAdminPage } from '../../utils/admin'
const adminStore=useAdminStore();const loading=ref(true);const errorMessage=ref('');const filters=reactive({order_no:'',user_id:'',status:null});const statusIndex=ref(0);const statusOptions=[{label:'全部状态',value:null},{label:'待支付',value:'pending'},{label:'已支付',value:'paid'}];const result=reactive({items:[],total:0,page:1,page_size:20})
onShow(async()=>{if(await requireAdminPage(adminStore))await loadOrders()})
async function loadOrders(){const userId=filters.user_id===''?null:normalizeInteger(filters.user_id);if(filters.user_id!==''&&(userId===null||userId<1)){errorMessage.value='用户 ID 需要是正整数';return}loading.value=true;errorMessage.value='';try{Object.assign(result,await adminApi.orders({order_no:filters.order_no,user_id:userId,status:filters.status,page:result.page,page_size:result.page_size}))}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function search(){result.page=1;loadOrders()}function reset(){Object.assign(filters,{order_no:'',user_id:'',status:null});statusIndex.value=0;result.page=1;loadOrders()}function changeStatus(event){statusIndex.value=Number(event.detail.value);filters.status=statusOptions[statusIndex.value].value}function changePage(page){result.page=page;loadOrders()}function openDetail(id){uni.navigateTo({url:`/pages/admin/order-detail?orderId=${id}`})}
</script>

<style scoped>
.orders-table{min-width:1120px}.orders-table .admin-table-row{grid-template-columns:1.5fr 1.45fr 1.05fr .7fr .75fr 1.05fr .55fr}.order-filters .admin-filter-field:nth-child(2){width:130px;min-width:130px}@media(max-width:760px){.orders-table{min-width:0}.order-filters .admin-filter-field:nth-child(2){width:auto;min-width:0}}
</style>
