import { API_BASE } from '../config'
import { STORAGE_KEYS, clearSessionStorage } from './storage'

function getErrorMessage(payload, fallback = '请求失败，请稍后重试') {
  const detail = payload?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc?.at(-1) || '参数'}：${item.msg || '格式错误'}`).join('；')
  }
  return payload?.message || fallback
}

function createRequestError(payload, statusCode, fallback) {
  const error = new Error(getErrorMessage(payload, fallback))
  error.statusCode = statusCode
  error.payload = payload
  return error
}

function handleUnauthorized(redirectUrl) {
  clearSessionStorage()
  uni.showToast({ title: '登录已失效，请重新登录', icon: 'none' })
  setTimeout(() => uni.reLaunch({ url: redirectUrl }), 350)
}

export function request({
  url,
  method = 'GET',
  data,
  timeout = 20000,
  auth = true,
  unauthorizedUrl = '/pages/auth/auth',
}) {
  const token = uni.getStorageSync(STORAGE_KEYS.accessToken)
  const header = { 'Content-Type': 'application/json' }
  if (auth && token) header.Authorization = `Bearer ${token}`
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${url}`, method, data, timeout, header,
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(response.data)
        if (response.statusCode === 401) handleUnauthorized(unauthorizedUrl)
        reject(createRequestError(response.data, response.statusCode))
      },
      fail(error) {
        reject(new Error(error.errMsg?.includes('timeout') ? '请求超时，请稍后重试' : '无法连接后端服务'))
      },
    })
  })
}

export function uploadFile({
  url,
  filePath,
  name = 'file',
  timeout = 60000,
  unauthorizedUrl = '/pages/auth/auth',
}) {
  const token = uni.getStorageSync(STORAGE_KEYS.accessToken)
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE}${url}`, filePath, name, timeout,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success(response) {
        let payload = response.data
        try { payload = JSON.parse(response.data) } catch (_) {}
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(payload)
        if (response.statusCode === 401) handleUnauthorized(unauthorizedUrl)
        reject(createRequestError(payload, response.statusCode, '文件上传失败'))
      },
      fail(error) {
        reject(new Error(error.errMsg?.includes('timeout') ? '上传超时，请稍后重试' : '文件上传失败'))
      },
    })
  })
}
