import { request, uploadFile } from '../utils/request'

function toQuery(params = {}) {
  const query = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')
  return query ? `?${query}` : ''
}

const adminRequest = (options) => request({
  timeout: 15000,
  unauthorizedUrl: '/pages/admin/login',
  ...options,
})

export const authApi = {
  sendCode: (email) => request({ url: `/auth/code?email=${encodeURIComponent(email)}`, auth: false }),
  register: (data) => request({ url: '/auth/register', method: 'POST', data, auth: false }),
  login: (data) => request({ url: '/auth/login', method: 'POST', data, auth: false }),
}
export const namingApi = {
  generate: (data) => request({ url: '/name/generate', method: 'POST', data, timeout: 180000 }),
  feedback: (data) => request({ url: '/name/feedback', method: 'POST', data, timeout: 180000 }),
}
export const accountApi = {
  balance: () => request({ url: '/credit/balance' }),
  sendTestEmail: () => request({ url: '/email', method: 'POST', timeout: 30000, auth: false }),
}
export const knowledgeApi = { upload: (filePath) => uploadFile({ url: '/knowledge/upload', filePath }) }
export const logoApi = {
  generate: (data) => request({ url: '/logos/generate', method: 'POST', data, timeout: 210000 }),
}
export const packageApi = {
  list: (type) => request({ url: `/package/list${type ? `?type=${encodeURIComponent(type)}` : ''}`, auth: false }),
  detail: (id) => request({ url: `/package/package/${id}`, auth: false }),
  createOrder: (packageId) => request({ url: '/pay/create_order', method: 'POST', data: { package_id: packageId } }),
}

export const adminApi = {
  me: () => adminRequest({ url: '/admin/me' }),
  dashboard: () => adminRequest({ url: '/admin/dashboard' }),
  users: (params) => adminRequest({ url: `/admin/users${toQuery(params)}` }),
  userDetail: (id) => adminRequest({ url: `/admin/users/${id}` }),
  updateUserStatus: (id, data) => adminRequest({
    url: `/admin/users/${id}/status`, method: 'PATCH', data,
  }),
  adjustUserCredit: (id, data) => adminRequest({
    url: `/admin/users/${id}/credits/adjust`, method: 'POST', data,
  }),
  packages: (params) => adminRequest({ url: `/admin/packages${toQuery(params)}` }),
  createPackage: (data) => adminRequest({ url: '/admin/packages', method: 'POST', data }),
  updatePackage: (id, data) => adminRequest({
    url: `/admin/packages/${id}`, method: 'PATCH', data,
  }),
  orders: (params) => adminRequest({ url: `/admin/orders${toQuery(params)}` }),
  orderDetail: (id) => adminRequest({ url: `/admin/orders/${id}` }),
  auditLogs: (params) => adminRequest({ url: `/admin/audit-logs${toQuery(params)}` }),
}
