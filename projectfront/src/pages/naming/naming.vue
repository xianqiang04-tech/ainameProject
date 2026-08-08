<template>
  <view class="page-shell">
    <BrandHeader />
    <view class="page-content naming-layout">
      <view class="panel naming-form-panel">
        <view class="panel-heading">
          <view><text class="section-title">开始一次命名</text><text class="section-note">信息越具体，名字越贴近你的想法。</text></view>
          <WandSparkles :size="28" :stroke-width="1.6" />
        </view>

        <view class="form-group first-group">
          <text class="field-label">命名类型</text>
          <view class="segmented-control category-control">
            <button v-for="item in categories" :key="item" class="segment-item" :class="{ active: form.category === item }" @click="setCategory(item)">{{ item }}</button>
          </view>
        </view>

        <template v-if="form.category === '人名'">
          <view class="form-grid">
            <view class="form-group">
              <text class="field-label">姓氏</text>
              <input v-model.trim="form.surname" class="input-control" maxlength="4" placeholder="例如：林" />
            </view>
            <view class="form-group">
              <text class="field-label">性别</text>
              <view class="segmented-control three-columns">
                <button v-for="item in genders" :key="item" class="segment-item" :class="{ active: form.gender === item }" @click="form.gender = item">{{ item }}</button>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="field-label">名字字数</text>
            <view class="segmented-control three-columns">
              <button v-for="item in lengths" :key="item" class="segment-item" :class="{ active: form.length === item }" @click="form.length = item">{{ item }}</button>
            </view>
          </view>
        </template>

        <view class="form-group">
          <text class="field-label">其他要求</text>
          <textarea v-model="form.other" class="textarea-control" maxlength="300" placeholder="例如：希望沉稳但不老气，带有山水意象，适合科技行业…" />
          <text class="char-count">{{ form.other.length }}/300</text>
        </view>

        <view class="form-group">
          <text class="field-label">排除词</text>
          <view class="exclude-row">
            <input v-model.trim="excludeDraft" class="input-control" placeholder="输入不希望出现的字词" @confirm="addExclude" />
            <button class="add-button" @click="addExclude"><Plus :size="18" /><text>添加</text></button>
          </view>
          <view v-if="form.exclude.length" class="tag-list">
            <button v-for="(word, index) in form.exclude" :key="word" class="tag" @click="removeExclude(index)"><text>{{ word }}</text><X :size="14" /></button>
          </view>
        </view>

        <button class="primary-button generate-button" :disabled="loading" @click="generate">
          <LoaderCircle v-if="loading" class="spin" :size="20" /><Sparkles v-else :size="20" />
          <text>{{ loading ? '正在推敲名字，请稍候…' : '生成名字方案' }}</text>
        </button>
        <view v-if="errorMessage" class="status-message error">{{ errorMessage }}</view>
      </view>

      <view class="results-column">
        <view v-if="loading && !results.length" class="panel waiting-state">
          <LoaderCircle class="spin waiting-icon" :size="34" />
          <text class="waiting-title">正在组织名字方案</text>
          <text class="section-note">这一步可能需要一两分钟，请保持页面打开。</text>
        </view>
        <view v-else-if="!results.length" class="panel empty-state">
          <view class="empty-icon"><BookOpenText :size="30" /></view>
          <text class="waiting-title">名字结果会出现在这里</text>
          <text class="section-note">每个结果都会包含出处、寓意和推荐域名。</text>
        </view>
        <template v-else>
          <view class="results-heading"><view><text class="section-title">本轮名字方案</text><text class="section-note">共 {{ results.length }} 个结果，可继续提出修改意见。</text></view><text class="round-label">{{ form.category }}</text></view>
          <view v-for="(item, index) in results" :key="`${item.name}-${index}`" class="name-card">
            <view class="name-card-top"><text class="name-index">0{{ index + 1 }}</text><text class="name-value">{{ item.name }}</text></view>
            <view class="name-detail"><text>出处</text><text>{{ item.reference }}</text></view>
            <view class="name-detail"><text>寓意</text><text>{{ item.moral }}</text></view>
            <button class="domain-row" @click="copyDomain(item.domain)">
              <Globe2 :size="17" /><text class="domain-value">{{ item.domain }}</text><text class="domain-status">{{ item.domain_status }}</text><Copy :size="15" />
            </button>
          </view>
          <view v-if="threadId" class="panel feedback-panel">
            <text class="feedback-title">还想怎么调整？</text>
            <textarea v-model="feedback" class="textarea-control" maxlength="300" placeholder="例如：整体更简洁一些，避免生僻字，保留自然意象…" />
            <button class="secondary-button feedback-button" :disabled="feedbackLoading" @click="submitFeedback">
              <LoaderCircle v-if="feedbackLoading" class="spin" :size="18" /><RefreshCw v-else :size="18" />
              <text>{{ feedbackLoading ? '正在重新推敲…' : '按意见重新生成' }}</text>
            </button>
          </view>
        </template>
      </view>
    </view>
    <BottomNav active="naming" />
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { WandSparkles, Plus, X, LoaderCircle, Sparkles, BookOpenText, Globe2, Copy, RefreshCw } from '@lucide/vue'
import BrandHeader from '../../components/BrandHeader.vue'
import BottomNav from '../../components/BottomNav.vue'
import { namingApi } from '../../api'
import { useAuthStore } from '../../stores/auth'
import { requireAuth } from '../../utils/storage'

const categories = ['人名','企业名','宠物名']
const genders = ['男','女','不限']
const lengths = ['单字','两字','不限']
const authStore = useAuthStore()
const form = reactive({ category:'人名', surname:'', gender:'不限', length:'不限', other:'', exclude:[] })
const excludeDraft = ref('')
const loading = ref(false)
const feedbackLoading = ref(false)
const errorMessage = ref('')
const results = ref([])
const threadId = ref('')
const feedback = ref('')

onShow(async () => { if (!requireAuth()) return; try { await authStore.refreshBalance() } catch (_) {} })
function setCategory(category) { form.category = category; if (category !== '人名') { form.surname=''; form.gender='不限'; form.length='不限' } }
function addExclude() { const words=excludeDraft.value.split(/[，,、\s]+/).filter(Boolean); words.forEach((word) => { if (!form.exclude.includes(word)) form.exclude.push(word) }); excludeDraft.value='' }
function removeExclude(index) { form.exclude.splice(index,1) }
function validate() { if (form.category === '人名' && !form.surname) return '生成人名时，请先填写姓氏'; return '' }
function payload() { return { category:form.category, surname:form.category==='人名'?form.surname:'', gender:form.category==='人名'?form.gender:'不限', length:form.category==='人名'?form.length:'不限', other:form.other, exclude:form.exclude } }
async function generate() {
  const message=validate(); if (message) { errorMessage.value=message; return }
  if (authStore.balance === 0) { uni.showModal({ title:'起名额度不足', content:'前往套餐页购买额度后再继续。', confirmText:'查看套餐', success:({confirm}) => { if (confirm) uni.navigateTo({ url:'/pages/packages/packages' }) } }); return }
  loading.value=true; errorMessage.value=''
  try { const data=await namingApi.generate(payload()); results.value=data.names||[]; threadId.value=data.thread_id||''; feedback.value=''; await authStore.refreshBalance() }
  catch(error) { errorMessage.value=error.message }
  finally { loading.value=false }
}
async function submitFeedback() {
  if (!feedback.value.trim()) return uni.showToast({ title:'请先填写修改意见', icon:'none' })
  if (authStore.balance === 0) { uni.navigateTo({ url:'/pages/packages/packages' }); return }
  feedbackLoading.value=true; errorMessage.value=''
  try { const data=await namingApi.feedback({ thread_id:threadId.value, category:form.category, feedback:feedback.value.trim() }); results.value=data.names||[]; threadId.value=data.thread_id||threadId.value; feedback.value=''; await authStore.refreshBalance(); uni.pageScrollTo({ scrollTop:0, duration:300 }) }
  catch(error) { errorMessage.value=error.message }
  finally { feedbackLoading.value=false }
}
function copyDomain(domain) { if (!domain) return; uni.setClipboardData({ data:domain, success:() => uni.showToast({ title:'域名已复制', icon:'none' }) }) }
</script>

<style scoped>
.naming-layout { display:grid; grid-template-columns:minmax(0, .86fr) minmax(0, 1.14fr); gap:28rpx; align-items:start; }
.panel-heading, .results-heading { display:flex; align-items:flex-start; justify-content:space-between; gap:24rpx; }
.panel-heading svg { color:#16836b; }
.first-group { margin-top:34rpx; }
.category-control, .three-columns { grid-template-columns:repeat(3,minmax(0,1fr)); }
.form-grid { display:grid; grid-template-columns:1fr 1.35fr; gap:22rpx; }
.char-count { display:block; margin-top:8rpx; color:#929a96; font-size:22rpx; text-align:right; }
.exclude-row { display:grid; grid-template-columns:minmax(0,1fr) 138rpx; gap:12rpx; }
.add-button { display:flex; min-height:88rpx; align-items:center; justify-content:center; gap:8rpx; border:1px solid #b9cbc4; border-radius:6px; background:#edf6f2; color:#176b57; font-size:25rpx; }
.tag-list { display:flex; flex-wrap:wrap; gap:12rpx; margin-top:18rpx; }
.tag { display:flex; min-height:52rpx; align-items:center; gap:8rpx; border-radius:5px; background:#eef2f0; padding:0 14rpx; color:#47534e; font-size:23rpx; }
.generate-button { width:100%; margin-top:36rpx; }
.spin { animation:spin .85s linear infinite; } @keyframes spin { to { transform:rotate(360deg); } }
.results-column { min-width:0; }
.waiting-state, .empty-state { display:flex; min-height:480rpx; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
.waiting-icon { margin-bottom:24rpx; color:#16836b; }
.empty-icon { display:flex; width:84rpx; height:84rpx; align-items:center; justify-content:center; margin-bottom:22rpx; border-radius:50%; background:#edf3f0; color:#4f7167; }
.waiting-title { display:block; margin-bottom:10rpx; color:#29342f; font-size:30rpx; font-weight:700; }
.round-label { flex:0 0 auto; border-radius:5px; background:#eaf4f0; padding:10rpx 16rpx; color:#126b57; font-size:23rpx; }
.name-card { margin-top:18rpx; border:1px solid #dce3df; border-radius:8px; background:#fff; padding:30rpx; }
.name-card-top { display:flex; align-items:baseline; gap:18rpx; padding-bottom:22rpx; border-bottom:1px solid #edf0ee; }
.name-index { color:#c75649; font-size:21rpx; font-weight:700; }
.name-value { color:#18201c; font-size:44rpx; font-weight:760; }
.name-detail { display:grid; grid-template-columns:82rpx minmax(0,1fr); gap:16rpx; margin-top:22rpx; line-height:1.7; }
.name-detail > text:first-child { color:#76807b; font-size:23rpx; }
.name-detail > text:last-child { color:#343e39; font-size:26rpx; }
.domain-row { display:flex; width:100%; min-height:68rpx; align-items:center; gap:10rpx; margin-top:24rpx; border-radius:6px; background:#f1f5f3; padding:0 18rpx; color:#40675c; font-size:23rpx; text-align:left; }
.domain-value { min-width:0; flex:1; overflow:hidden; color:#185d4c; text-overflow:ellipsis; white-space:nowrap; }
.domain-status { flex:0 0 auto; color:#77817c; font-size:21rpx; }
.feedback-panel { margin-top:22rpx; }
.feedback-title { display:block; margin-bottom:20rpx; font-size:29rpx; font-weight:700; }
.feedback-button { width:100%; margin-top:20rpx; }
@media (max-width:820px) { .naming-layout { display:block; } .results-column { margin-top:28rpx; } .waiting-state,.empty-state { min-height:340rpx; } }
@media (max-width:420px) { .form-grid { display:block; } .exclude-row { grid-template-columns:minmax(0,1fr) 110rpx; } .add-button text { display:none; } .name-detail { grid-template-columns:62rpx minmax(0,1fr); } .domain-status { display:none; } }
</style>
