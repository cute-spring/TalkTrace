import axios from 'axios'
import type { AxiosResponse } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API响应类型
interface ApiResponse<T = any> {
  success: boolean
  data: T
  error?: {
    code: string
    message: string
    details?: any
  }
}

// 历史记录相关API
export const historyService = {
  search: (params: any) => apiClient.get<ApiResponse>('/v1/history/search', { params }),
  getSessionDetails: (sessionId: string) =>
    apiClient.get<ApiResponse>(`/v1/history/sessions/${sessionId}`),
  getModels: () => apiClient.get<ApiResponse>('/v1/history/models'),
  checkHealth: () => apiClient.get<ApiResponse>('/v1/history/health'),
}

// 导入相关API
export const importService = {
  validateSessions: (data: { session_ids: string[] }) =>
    apiClient.post<ApiResponse>('/v1/import/validate-sessions', data),
  preview: (data: { session_ids: string[] }) =>
    apiClient.post<ApiResponse>('/v1/import/preview', data),
  execute: (data: { session_ids: string[]; defaultOwner?: string; defaultPriority?: string; defaultDifficulty?: string; includeAnalysis?: boolean }) =>
    apiClient.post<ApiResponse>('/v1/import/execute', data),
  getProgress: (taskId: string) =>
    apiClient.get<ApiResponse>(`/v1/import/progress/${taskId}`),
  getTasks: (params?: { page?: number; pageSize?: number }) =>
    apiClient.get<ApiResponse>('/v1/import/tasks', { params }),
}

// 测试用例相关API
export const testCaseService = {
  getList: (params?: any) =>
    apiClient.get<ApiResponse>('/v1/test-cases/', { params }),
  getById: (id: string) =>
    apiClient.get<ApiResponse>(`/v1/test-cases/${id}`),
  create: (data: any) =>
    apiClient.post<ApiResponse>('/v1/test-cases/', data),
  update: (id: string, data: any) =>
    apiClient.put<ApiResponse>(`/v1/test-cases/${id}`, data),
  delete: (id: string) =>
    apiClient.delete<ApiResponse>(`/v1/test-cases/${id}`),
  batchOperation: (data: { action: string; ids: string[]; data?: any }) =>
    apiClient.post<ApiResponse>('/v1/test-cases/batch', data),
  getStatistics: () =>
    apiClient.get<ApiResponse>('/v1/test-cases/statistics/overview'),
  getTags: () =>
    apiClient.get<ApiResponse>('/v1/test-cases/tags'),
}

// 标签相关API
export const tagService = {
  getList: () => apiClient.get<ApiResponse>('/v1/tags'),
  create: (data: { name: string; color?: string }) =>
    apiClient.post<ApiResponse>('/v1/tags', data),
  update: (id: string, data: { name: string; color?: string }) =>
    apiClient.put<ApiResponse>(`/v1/tags/${id}`, data),
  delete: (id: string) =>
    apiClient.delete<ApiResponse>(`/v1/tags/${id}`),
}

// 分析相关API
export const analyticsService = {
  getOverview: (params?: { startDate?: string; endDate?: string }) =>
    apiClient.get<ApiResponse>('/v1/analytics/overview', { params }),
  getHealth: () =>
    apiClient.get<ApiResponse>('/v1/analytics/health'),
}

export default apiClient