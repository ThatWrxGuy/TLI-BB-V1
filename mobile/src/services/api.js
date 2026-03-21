import axios from 'axios'
import AsyncStorage from '@react-native-async-storage/async-storage'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      AsyncStorage.removeItem('token')
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', new URLSearchParams({ username: email, password })),
  
  signup: (email, password, fullName) => 
    api.post('/auth/signup', { email, password, full_name: fullName }),
  
  logout: () => api.post('/auth/logout'),
  
  getMe: () => api.get('/auth/me'),
}

// Dashboard API
export const dashboardAPI = {
  getDashboard: () => api.get('/dashboard'),
  getOverview: () => api.get('/dashboard/overview'),
  getGoals: () => api.get('/dashboard/goals'),
  createGoal: (title, description) => api.post('/dashboard/goals', null, { params: { title, description } }),
  getTasks: () => api.get('/dashboard/tasks'),
  createTask: (title, description, priority) => 
    api.post('/dashboard/tasks', null, { params: { title, description, priority } }),
  toggleTask: (id) => api.patch(`/dashboard/tasks/${id}/toggle`),
  getRecommendations: () => api.get('/dashboard/recommendations'),
  getDomainScores: () => api.get('/dashboard/domain-scores'),
  getMood: () => api.get('/dashboard/mood'),
  logMood: (mood, note) => api.post('/dashboard/mood', { mood, note }),
}

// Finance API
export const financeAPI = {
  getAccounts: () => api.get('/finance/accounts'),
  linkAccount: (publicToken) => api.post('/finance/plaid/link', { public_token: publicToken }),
  getTransactions: (params) => api.get('/finance/transactions', { params }),
  getInsights: (days) => api.get('/finance/insights', { params: { days } }),
  getNetWorth: () => api.get('/finance/net-worth'),
}

// Profile API
export const profileAPI = {
  getProfile: () => api.get('/profile'),
  updateProfile: (data) => api.patch('/profile', data),
  getSettings: () => api.get('/profile/settings'),
  changePassword: (currentPassword, newPassword) => 
    api.post('/profile/password', { current_password: currentPassword, new_password: newPassword }),
}

// Upload API (Web only)
export const uploadAPI = {
  uploadAvatar: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteAvatar: () => api.delete('/upload/avatar'),
  uploadFile: async (file, category) => {
    const formData = new FormData()
    formData.append('file', file)
    if (category) formData.append('category', category)
    return api.post('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  listFiles: (category) => api.get('/upload/files', { params: { category } }),
  deleteFile: (fileId) => api.delete(`/upload/files/${fileId}`),
}

export default api
