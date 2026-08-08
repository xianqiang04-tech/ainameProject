<template>
  <AdminShell active="packages" title="套餐管理" subtitle="维护套餐价格、次数和启用状态">
    <template #actions><button class="admin-button primary" @click="openCreate"><Plus :size="16"/><text>新增套餐</text></button></template>
    <view class="admin-filter-panel">
      <view class="admin-filter-field grow"><text class="admin-filter-label">套餐名称</text><input v-model.trim="filters.keyword" class="admin-input" placeholder="输入套餐名称" @confirm="search"/></view>
      <view class="admin-filter-field"><text class="admin-filter-label">套餐状态</text><picker :range="statusOptions" range-key="label" :value="statusIndex" @change="changeStatus"><view class="admin-select"><text>{{statusOptions[statusIndex].label}}</text><ChevronDown :size="15"/></view></picker></view>
      <button class="admin-button primary" :disabled="loading" @click="search"><Search :size="16"/><text>查询</text></button>
      <button class="admin-button" :disabled="loading" @click="reset"><RotateCcw :size="16"/><text>重置</text></button>
    </view>
    <view class="admin-data-panel">
      <view v-if="loading" class="admin-state"><LoaderCircle class="admin-spin" :size="26"/><strong>正在读取套餐</strong></view>
      <view v-else-if="errorMessage" class="admin-state"><AlertCircle :size="28"/><strong>套餐列表加载失败</strong><text>{{errorMessage}}</text><button class="admin-button" @click="loadPackages">重新加载</button></view>
      <view v-else-if="!result.items.length" class="admin-state"><PackageOpen :size="30"/><strong>没有匹配的套餐</strong><text>可以调整筛选条件或创建新套餐。</text></view>
      <view v-else class="admin-table-scroll"><view class="admin-table packages-table">
        <view class="admin-table-row header"><view class="admin-table-cell">套餐</view><view class="admin-table-cell">价格</view><view class="admin-table-cell">包含次数</view><view class="admin-table-cell">状态</view><view class="admin-table-cell">创建时间</view><view class="admin-table-cell"></view></view>
        <view v-for="item in result.items" :key="item.id" class="admin-table-row">
          <view class="admin-table-cell" data-label="套餐"><view><strong>{{item.name}}</strong><small>ID {{item.id}}</small></view></view>
          <view class="admin-table-cell" data-label="价格"><strong>{{formatMoney(item.price)}}</strong></view>
          <view class="admin-table-cell" data-label="包含次数"><text>{{item.credit_count}} 次</text></view>
          <view class="admin-table-cell" data-label="状态"><StatusBadge type="package" :value="item.is_active"/></view>
          <view class="admin-table-cell" data-label="创建时间"><text>{{formatDateTime(item.created_at)}}</text></view>
          <view class="admin-table-cell admin-table-actions" data-label="操作"><button class="admin-link-button" @click="openEdit(item)"><Pencil :size="15"/><text>编辑</text></button></view>
        </view>
      </view></view>
      <AdminPagination :page="result.page" :page-size="result.page_size" :total="result.total" :loading="loading" @change="changePage"/>
    </view>

    <AdminModal :open="modalOpen" :title="editingId?'编辑套餐':'新增套餐'" :subtitle="editingId?'修改内容会记录到审计日志':'创建一个可供用户购买的套餐'" @close="closeModal">
      <view class="admin-form-grid">
        <view class="admin-form-field full"><text class="admin-form-label">套餐名称</text><input v-model="form.name" class="admin-input" maxlength="100" placeholder="例如：基础套餐"/></view>
        <view class="admin-form-field"><text class="admin-form-label">价格（元）</text><input v-model.trim="form.price" class="admin-input" type="digit" placeholder="0.00"/></view>
        <view class="admin-form-field"><text class="admin-form-label">包含次数</text><input v-model.trim="form.credit_count" class="admin-input" type="number" placeholder="正整数"/></view>
        <view class="admin-form-field full"><text class="admin-form-label">启用状态</text><view class="switch-line"><switch :checked="form.is_active" color="#167861" @change="form.is_active=$event.detail.value"/><text>{{form.is_active?'套餐对用户可见':'套餐暂不对用户开放'}}</text></view></view>
        <view class="admin-form-field full"><text class="admin-form-label">{{editingId?'修改原因':'创建说明（可选）'}}</text><textarea v-model="form.reason" class="admin-textarea" maxlength="500" :placeholder="editingId?'请输入修改原因':'可填写创建说明'"/></view>
      </view>
      <view v-if="modalError" class="admin-error">{{modalError}}</view>
      <template #footer><button class="admin-button" :disabled="submitting" @click="closeModal">取消</button><button class="admin-button primary" :disabled="submitting" @click="submit"><LoaderCircle v-if="submitting" class="admin-spin" :size="16"/><text>{{editingId?'保存修改':'创建套餐'}}</text></button></template>
    </AdminModal>
  </AdminShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { AlertCircle, ChevronDown, LoaderCircle, PackageOpen, Pencil, Plus, RotateCcw, Search } from '@lucide/vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminPagination from '../../components/admin/AdminPagination.vue'
import AdminShell from '../../components/admin/AdminShell.vue'
import StatusBadge from '../../components/admin/StatusBadge.vue'
import { adminApi } from '../../api'
import { useAdminStore } from '../../stores/admin'
import { formatDateTime, formatMoney, normalizeInteger, requireAdminPage } from '../../utils/admin'

const adminStore=useAdminStore();const loading=ref(true);const errorMessage=ref('');const filters=reactive({keyword:'',is_active:null});const statusIndex=ref(0)
const statusOptions=[{label:'全部状态',value:null},{label:'已启用',value:true},{label:'已停用',value:false}];const result=reactive({items:[],total:0,page:1,page_size:20})
const modalOpen=ref(false);const editingId=ref(null);const submitting=ref(false);const modalError=ref('');const form=reactive({name:'',price:'',credit_count:'',is_active:true,reason:''})
onShow(async()=>{if(await requireAdminPage(adminStore))await loadPackages()})
async function loadPackages(){loading.value=true;errorMessage.value='';try{Object.assign(result,await adminApi.packages({keyword:filters.keyword,is_active:filters.is_active,page:result.page,page_size:result.page_size}))}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function search(){result.page=1;loadPackages()}function reset(){filters.keyword='';filters.is_active=null;statusIndex.value=0;result.page=1;loadPackages()}function changeStatus(event){statusIndex.value=Number(event.detail.value);filters.is_active=statusOptions[statusIndex.value].value}function changePage(page){result.page=page;loadPackages()}
function resetForm(){Object.assign(form,{name:'',price:'',credit_count:'',is_active:true,reason:''});modalError.value=''}
function openCreate(){editingId.value=null;resetForm();modalOpen.value=true}
function openEdit(item){editingId.value=item.id;Object.assign(form,{name:item.name,price:String(item.price),credit_count:String(item.credit_count),is_active:item.is_active,reason:''});modalError.value='';modalOpen.value=true}
function closeModal(){if(submitting.value)return;modalOpen.value=false;modalError.value=''}
function validate(){const name=form.name.trim();const credits=normalizeInteger(form.credit_count);if(!name)return'请输入套餐名称';if(!/^\d{1,8}(\.\d{1,2})?$/.test(form.price)||Number(form.price)<0)return'价格需要是 0 至 99999999.99 的金额';if(credits===null||credits<1)return'包含次数需要是大于 0 的整数';if(editingId.value&&!form.reason.trim())return'请输入修改原因';return''}
async function submit(){const message=validate();if(message){modalError.value=message;return}submitting.value=true;modalError.value='';const payload={name:form.name.trim(),price:Number(form.price).toFixed(2),credit_count:Number(form.credit_count),is_active:form.is_active,reason:form.reason.trim()||null};try{if(editingId.value)await adminApi.updatePackage(editingId.value,{...payload,reason:form.reason.trim()});else await adminApi.createPackage(payload);modalOpen.value=false;uni.showToast({title:editingId.value?'套餐已更新':'套餐已创建',icon:'success'});await loadPackages()}catch(error){modalError.value=error.message}finally{submitting.value=false}}
</script>

<style scoped>
.packages-table{min-width:930px}.packages-table .admin-table-row{grid-template-columns:minmax(190px,1.7fr) .8fr .8fr .8fr 1.25fr .6fr}.switch-line{display:flex;min-height:40px;align-items:center;gap:12px;color:#68756f;font-size:12px}@media(max-width:760px){.packages-table{min-width:0}}
</style>
