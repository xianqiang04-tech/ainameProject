<template>
  <AdminShell active="users" title="用户详情" subtitle="查看账号、次数和订单统计">
    <template #actions><button class="admin-button" @click="back"><ArrowLeft :size="16"/><text>返回用户列表</text></button></template>
    <view v-if="loading" class="admin-data-panel"><view class="admin-state"><LoaderCircle class="admin-spin" :size="26"/><strong>正在读取用户详情</strong></view></view>
    <view v-else-if="errorMessage" class="admin-data-panel"><view class="admin-state"><AlertCircle :size="28"/><strong>用户详情加载失败</strong><text>{{errorMessage}}</text><button class="admin-button" @click="loadUser">重新加载</button></view></view>
    <template v-else-if="user">
      <view class="profile-strip">
        <view class="profile-avatar"><UserRound :size="26"/></view>
        <view class="profile-copy"><text>{{user.username}}</text><text>{{user.email}} · ID {{user.id}}</text></view>
        <view class="profile-badges"><text class="role-label" :class="user.role">{{user.role==='admin'?'管理员':'普通用户'}}</text><StatusBadge type="active" :value="user.is_active"/></view>
      </view>
      <view class="stats-grid">
        <view><text>起名余额</text><text>{{user.balance}}</text><text>次</text></view>
        <view><text>Logo 余额</text><text>{{user.logo_balance}}</text><text>次</text></view>
        <view><text>累计使用</text><text>{{user.total_used}}</text><text>次</text></view>
        <view><text>Logo 已用</text><text>{{user.logo_total_used}}</text><text>次</text></view>
        <view><text>累计充值</text><text>{{user.total_recharged}}</text><text>次</text></view>
        <view><text>订单总数</text><text>{{user.order_count}}</text><text>笔</text></view>
        <view><text>已支付订单</text><text>{{user.paid_order_count}}</text><text>笔</text></view>
      </view>
      <view class="admin-detail-band user-info-band">
        <view class="admin-detail-section"><text class="admin-detail-title">账号信息</text><view class="admin-detail-grid">
          <view class="admin-detail-item"><text>创建时间</text><text>{{formatDateTime(user.created_at)}}</text></view>
          <view class="admin-detail-item"><text>最近登录</text><text>{{formatDateTime(user.last_login_at)}}</text></view>
          <view class="admin-detail-item"><text>账号状态</text><text>{{user.is_active?'允许登录':'禁止登录'}}</text></view>
        </view></view>
        <view class="admin-detail-section"><view class="operation-heading"><view><text>账号操作</text><text>{{canManage?'所有变更都需要填写原因并写入审计日志':'管理员账号不允许在第一版中修改'}}</text></view><view v-if="canManage"><button class="admin-button" @click="openCreditModal"><BadgePlus :size="16"/><text>调整次数</text></button><button class="admin-button" :class="user.is_active?'danger':'primary'" @click="openStatusModal"><UserX v-if="user.is_active" :size="16"/><UserCheck v-else :size="16"/><text>{{user.is_active?'停用账号':'启用账号'}}</text></button></view></view></view>
      </view>
    </template>

    <AdminModal :open="statusModal" :title="user?.is_active?'停用用户':'启用用户'" subtitle="该操作会立即影响用户登录状态" @close="closeModals">
      <view class="admin-form-field"><text class="admin-form-label">操作原因</text><textarea v-model="statusReason" class="admin-textarea" maxlength="500" placeholder="请输入操作原因"/></view><view v-if="modalError" class="admin-error">{{modalError}}</view>
      <template #footer><button class="admin-button" :disabled="submitting" @click="closeModals">取消</button><button class="admin-button" :class="user?.is_active?'danger':'primary'" :disabled="submitting" @click="submitStatus"><LoaderCircle v-if="submitting" class="admin-spin" :size="16"/><text>确认{{user?.is_active?'停用':'启用'}}</text></button></template>
    </AdminModal>
    <AdminModal :open="creditModal" title="调整用户次数" subtitle="正数增加次数，负数扣减次数" @close="closeModals">
      <view class="credit-preview"><view><text>{{creditForm.account_type==='logo'?'当前 Logo 余额':'当前起名余额'}}</text><text>{{currentBalance}} 次</text></view><ArrowRight :size="18"/><view><text>调整后余额</text><text :class="{'negative':previewBalance<0}">{{previewBalance}} 次</text></view></view>
      <view class="admin-form-grid"><view class="admin-form-field full"><text class="admin-form-label">账户类型</text><picker :range="accountOptions" range-key="label" :value="accountIndex" @change="changeAccountType"><view class="admin-select"><text>{{accountOptions[accountIndex].label}}</text><ChevronDown :size="15"/></view></picker></view><view class="admin-form-field full"><text class="admin-form-label">变更次数</text><input v-model.trim="creditForm.change_count" class="admin-input" type="number" placeholder="例如 5 或 -2"/><text class="admin-form-note">单次调整范围 -100000 至 100000，不能为 0。</text></view><view class="admin-form-field full"><text class="admin-form-label">调整原因</text><textarea v-model="creditForm.reason" class="admin-textarea" maxlength="500" placeholder="请输入调整原因"/></view></view><view v-if="modalError" class="admin-error">{{modalError}}</view>
      <template #footer><button class="admin-button" :disabled="submitting" @click="closeModals">取消</button><button class="admin-button primary" :disabled="submitting||previewBalance<0" @click="submitCredit"><LoaderCircle v-if="submitting" class="admin-spin" :size="16"/><text>确认调整</text></button></template>
    </AdminModal>
  </AdminShell>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { AlertCircle, ArrowLeft, ArrowRight, BadgePlus, ChevronDown, LoaderCircle, UserCheck, UserRound, UserX } from '@lucide/vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminShell from '../../components/admin/AdminShell.vue'
import StatusBadge from '../../components/admin/StatusBadge.vue'
import { adminApi } from '../../api'
import { useAdminStore } from '../../stores/admin'
import { formatDateTime, normalizeInteger, requireAdminPage } from '../../utils/admin'

const adminStore=useAdminStore();const userId=ref(null);const user=ref(null);const loading=ref(true);const errorMessage=ref('')
const statusModal=ref(false);const creditModal=ref(false);const statusReason=ref('');const creditForm=reactive({change_count:'',account_type:'name',reason:''});const modalError=ref('');const submitting=ref(false)
const accountOptions=[{label:'起名额度',value:'name'},{label:'Logo 次数',value:'logo'}]
const accountIndex=computed(()=>Math.max(0,accountOptions.findIndex(option=>option.value===creditForm.account_type)))
function changeAccountType(event){creditForm.account_type=accountOptions[Number(event.detail.value)].value}
const canManage=computed(()=>user.value&&user.value.role!=='admin'&&user.value.id!==adminStore.profile?.id)
const currentBalance=computed(()=>creditForm.account_type==='logo'?(user.value?.logo_balance||0):(user.value?.balance||0))
const previewBalance=computed(()=>{const count=normalizeInteger(creditForm.change_count);return currentBalance.value+(count??0)})
onLoad(({userId:id})=>{userId.value=Number(id)||null})
onShow(async()=>{if(await requireAdminPage(adminStore)&&userId.value)await loadUser()})
async function loadUser(){loading.value=true;errorMessage.value='';try{user.value=await adminApi.userDetail(userId.value)}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
function back(){uni.navigateBack({fail:()=>uni.redirectTo({url:'/pages/admin/users'})})}
function openStatusModal(){statusReason.value='';modalError.value='';statusModal.value=true}
function openCreditModal(){creditForm.change_count='';creditForm.account_type='name';creditForm.reason='';modalError.value='';creditModal.value=true}
function closeModals(){if(submitting.value)return;statusModal.value=false;creditModal.value=false;modalError.value=''}
async function submitStatus(){const reason=statusReason.value.trim();if(!reason){modalError.value='请输入操作原因';return}submitting.value=true;modalError.value='';try{await adminApi.updateUserStatus(userId.value,{is_active:!user.value.is_active,reason});statusModal.value=false;uni.showToast({title:'账号状态已更新',icon:'success'});await loadUser()}catch(error){modalError.value=error.message}finally{submitting.value=false}}
async function submitCredit(){const change=normalizeInteger(creditForm.change_count);const reason=creditForm.reason.trim();if(change===null||change===0||change<-100000||change>100000){modalError.value='请输入 -100000 至 100000 之间的非零整数';return}if(!reason){modalError.value='请输入调整原因';return}if(previewBalance.value<0){modalError.value='调整后余额不能小于 0';return}submitting.value=true;modalError.value='';try{await adminApi.adjustUserCredit(userId.value,{change_count:change,account_type:creditForm.account_type,reason});creditModal.value=false;uni.showToast({title:'次数已调整',icon:'success'});await loadUser()}catch(error){modalError.value=error.message}finally{submitting.value=false}}
</script>

<style scoped>
.profile-strip{display:flex;align-items:center;gap:14px;border:1px solid #dfe5e2;border-radius:8px;background:#fff;padding:20px}.profile-avatar{display:flex;width:48px;height:48px;flex:0 0 auto;align-items:center;justify-content:center;border-radius:7px;background:#e8f3ef;color:#176f59}.profile-copy{min-width:0;flex:1}.profile-copy text:first-child{display:block;color:#202a25;font-size:18px;font-weight:730}.profile-copy text:last-child{display:block;overflow:hidden;margin-top:4px;color:#7b8781;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.profile-badges{display:flex;align-items:center;gap:8px}.role-label{display:inline-flex;height:24px;align-items:center;border:1px solid #d8dfdc;border-radius:5px;background:#f3f5f4;padding:0 8px;color:#65716b;font-size:11px;font-weight:650}.role-label.admin{border-color:#b8d9cc;background:#edf7f3;color:#176b57}.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-top:16px}.stats-grid>view{border:1px solid #dfe5e2;border-radius:8px;background:#fff;padding:17px}.stats-grid text:first-child{display:block;color:#78847e;font-size:11px}.stats-grid text:nth-child(2){font-size:24px;font-weight:750}.stats-grid text:last-child{margin-left:4px;color:#87928c;font-size:11px}.user-info-band{margin-top:16px}.operation-heading{display:flex;align-items:center;justify-content:space-between;gap:18px}.operation-heading>view:first-child text:first-child{display:block;color:#26312c;font-size:14px;font-weight:700}.operation-heading>view:first-child text:last-child{display:block;margin-top:5px;color:#839089;font-size:11px}.operation-heading>view:last-child{display:flex;gap:9px}.credit-preview{display:flex;align-items:center;justify-content:center;gap:24px;margin-bottom:20px;border:1px solid #e2e7e4;border-radius:7px;background:#f7f9f8;padding:16px}.credit-preview>view{text-align:center}.credit-preview text:first-child{display:block;color:#7b8781;font-size:11px}.credit-preview text:last-child{display:block;margin-top:5px;color:#26322d;font-size:18px;font-weight:750}.credit-preview text.negative{color:#b74638}@media(max-width:900px){.stats-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:760px){.profile-strip{align-items:flex-start}.profile-badges{flex-direction:column;align-items:flex-end}.stats-grid{grid-template-columns:1fr 1fr}.operation-heading{align-items:flex-start;flex-direction:column}.operation-heading>view:last-child{width:100%;flex-direction:column}.operation-heading>view:last-child button{width:100%}}@media(max-width:420px){.stats-grid{grid-template-columns:1fr}.credit-preview{gap:13px}}
</style>
