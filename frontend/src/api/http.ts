import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export const http = axios.create({
  baseURL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export type ApiError = {
  message: string
  status?: number
}

export function toApiError(err: unknown): ApiError {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status
    const message =
      typeof err.response?.data === 'string'
        ? err.response?.data
        : (err.response?.data as { message?: string })?.message
    return {
      message: message ?? 'Ошибка запроса',
      status,
    }
  }

  return { message: 'Неизвестная ошибка' }
}

