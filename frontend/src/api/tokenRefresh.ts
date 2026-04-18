import axios from 'axios'
import {
  getRefreshToken,
  setAccessTokenOnly,
  notifyAccessRefreshed,
} from './authTokens'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

const refreshClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken()
  if (!refresh) {
    return Promise.reject(new Error('Нет refresh-токена'))
  }
  const res = await refreshClient.post<{ access: string }>('/token/refresh/', { refresh })
  const access = res.data.access
  setAccessTokenOnly(access)
  notifyAccessRefreshed(access)
  return access
}
