<template>
  <AdminShell active="users" title="用户管理" subtitle="查询账号状态、余额与最近登录信息">
    <template #actions><button class="admin-button" :disabled="loading" @click="loadUsers"><RefreshCw :class="{'admin-spin':loading}" :size="16"/><text>刷新</text></button></template>
    <view class="admin-filter-panel">
      <view class="admin-filter-field grow"><text class="admin-filter-label">关键词</text><input v-model.trim="filters.keyword" class="admin-input" placeholder="邮箱或用户名" @confirm="search"/></view>
      <view class="admin-filter-field"><text class="admin-filter-label">账号状态</text><picker :range="statusOptions" range-key="label" :value="statusIndex" @change="changeStatus"><view class="admin-select"><text>{{statusOptions[statusIndex].label}}</text><ChevronDown :size="15"/></view></picker></view>
      <button class="admin-button primary" :disabled="loading" @click="search"><Search :size="16"/><text>查询</text></button>
      <button class="admin-button" :disabled="loading" @click="reset"><RotateCcw :size="16"/><text>重置</text></button>
    </view>

    <view class="admin-data-panel">
      <view v-if="loading" class="admin-state"><LoaderCircle class="admin-spin" :size="26"/><strong>正在读取用户</strong></view>
      <view v-else-if="errorMessage" class="admin-state"><AlertCircle :size="28"/><strong>用户列表加载失败</strong><text>{{errorMessage}}</text><button class="admin-button" @click="loadUsers">重新加载</button></view>
      <view v-else-if="!result.items.length" class="admin-state"><Users :size="30"/><strong>没有匹配的用户</strong><text>调整关键词或状态筛选后再试。</text></view>
      <view v-else class="admin-table-scroll"><view class="admin-table users-table">
        <view class="admin-table-row header"><view class="admin-table-cell">用户</view><view class="admin-table-cell">角色</view><view class="admin-table-cell">状态</view><view class="admin-table-cell">余额</view><view class="admin-table-cell">最近登录</view><view class="admin-table-cell"></view></view>
        <view v-for="user in result.items" :key="user.id" class="admin-table-row">
          <view class="admin-table-cell" data-label="用户"><view><strong>{{user.username}}</strong><small>{{user.email}} · ID {{user.id}}</small></view></view>
          <view class="admin-table-cell" data-label="角色"><text class="role-label" :class="user.role">{{user.role==='admin'?'管理员':'普通用户'}}</text></view>
          <view class="admin-table-cell" data-label="状态"><StatusBadge type="active" :value="user.is_active"/></view>
          <view class="admin-table-cell" data-label="余额"><strong>{{user.balance}} 次</strong></view>
          <view class="admin-table-cell" data-label="最近登录"><text>{{formatDateTime(user.last_login_at)}}</text></view>
          <view class="admin-table-cell admin-table-actions" data-label="操作"><button class="admin-link-button" @click="openDetail(user.id)"><Eye :size="15"/><text>详情</text></button></view>
        </view>
      </view></view>
      <AdminPagination :page="result.page" :page-size="result.page_size" :total="result.total" :loading="loading" @change="changePage"/>
    </view>
  </AdminShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { AlertCircle, ChevronDown, Eye, LoaderCircle, RefreshCw, RotateCcw, Search, Users } from '@lucide/vue'
import AdminPagination from '../../components/admin/AdminPagination.vue'
import AdminShell from '../../components/admin/AdminShell.vue'
import StatusBadge from '../../components/admin/StatusBadge.vue'
import { adminApi } from '../../api'
import { useAdminStore } from '../../stores/admin'
import { formatDateTime, requireAdminPage } from '../../utils/admin'

const adminStore=useAdminStore(); const loading=ref(true); const errorMessage=ref('')
const filters=reactive({keyword:'',is_active:null}); const statusIndex=ref(0)
const statusOptions=[{label:'全部状态',value:null},{label:'正常',value:true},{label:'已停用',value:false}]
const result=reactive({items:[],total:0,page:1,page_size:20})
onShow(async()=>{if(await requireAdminPage(adminStore))await loadUsers()})
async function loadUsers(){loading.value=true;errorMessage.value='';try{Object.assign(result,await adminApi.users({keyword:filters.keyword,is_active:filters.is_active,page:result.page,page_size:result.page_size}))}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function search(){result.page=1;loadUsers()}
function reset(){filters.keyword='';filters.is_active=null;statusIndex.value=0;result.page=1;loadUsers()}
function changeStatus(event){statusIndex.value=Number(event.detail.value);filters.is_active=statusOptions[statusIndex.value].value}
function changePage(page){result.page=page;loadUsers()}
function openDetail(id){uni.navigateTo({url:`/pages/admin/user-detail?userId=${id}`})}
</script>

<style scoped>
.users-table{min-width:940px}.users-table .admin-table-row{grid-template-columns:minmax(220px,2fr) .8fr .8fr .7fr 1.35fr .7fr}.role-label{display:inline-flex;height:24px;align-items:center;border:1px solid #d8dfdc;border-radius:5px;background:#f3f5f4;padding:0 8px;color:#65716b;font-size:11px;font-weight:650}.role-label.admin{border-color:#b8d9cc;background:#edf7f3;color:#176b57}@media(max-width:760px){.users-table{min-width:0}}
</style>
