import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { getAccessToken, getRefreshToken, clearAuthTokens } from './authTokens'
import { refreshAccessToken } from './tokenRefresh'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export const http = axios.create({
  baseURL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

let authFailureHandler: (() => void) | null = null

export function setAuthFailureHandler(handler: (() => void) | null) {
  authFailureHandler = handler
}

function isAuthPath(url?: string): boolean {
  if (!url) return false
  return url.includes('/token/') && !url.includes('/token/verify/')
}

http.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
    const status = error.response?.status

    if (status !== 401 || !original || original._retry) {
      return Promise.reject(error)
    }

    if (isAuthPath(original.url)) {
      return Promise.reject(error)
    }

    if (!getRefreshToken()) {
      return Promise.reject(error)
    }

    original._retry = true

    try {
      const access = await refreshAccessToken()
      original.headers.Authorization = `Bearer ${access}`
      return http(original)
    } catch {
      clearAuthTokens()
      authFailureHandler?.()
      return Promise.reject(error)
    }
  },
)

export type ApiError = {
  message: string
  status?: number
}

function extractDrfMessage(data: unknown): string | undefined {
  if (data == null) return undefined
  if (typeof data === 'string') return data
  if (typeof data !== 'object') return undefined
  const d = data as Record<string, unknown>
  if (typeof d.detail === 'string') return d.detail
  if (Array.isArray(d.detail)) return d.detail.map(String).join(' ')
  if (typeof d.message === 'string') return d.message
  if (Array.isArray(d.non_field_errors)) {
    return (d.non_field_errors as unknown[]).map(String).join(' ')
  }
  for (const key of Object.keys(d)) {
    const v = d[key]
    if (Array.isArray(v) && v.length) {
      const first = v[0]
      if (typeof first === 'string') {
        return `${key}: ${v.join(' ')}`
      }
    }
  }
  return undefined
}

export function toApiError(err: unknown): ApiError {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status
    const data = err.response?.data
    const message =
      extractDrfMessage(data) ??
      (typeof data === 'string' ? data : undefined) ??
      err.message ??
      'Ошибка запроса'
    return {
      message,
      status,
    }
  }

  if (err && typeof err === 'object' && 'message' in err && typeof (err as ApiError).message === 'string') {
    return err as ApiError
  }

  return { message: 'Неизвестная ошибка' }
}
