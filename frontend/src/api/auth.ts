import axios from 'axios'
import { http, toApiError } from './http'
import { setAuthTokens } from './authTokens'
import type { Role } from '../types/roles'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

/** Ответ SimpleJWT при выдаче пары токенов */
export type TokenPair = {
  access: string
  refresh: string
}

/** Профиль из GET/PATCH /api/v1/users/me/ */
export type UserProfile = {
  id: number
  email: string
  first_name: string
  last_name: string
  role: Role
  is_active: boolean
  date_joined: string
}

export type RegisterPayload = {
  email: string
  first_name: string
  last_name: string
  password: string
  role?: Role
}

const plainClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export async function registerUser(payload: RegisterPayload): Promise<{ user_id: number }> {
  try {
    const res = await plainClient.post<{ message: string; user_id: number }>('/v1/register/', payload)
    return { user_id: res.data.user_id }
  } catch (err) {
    throw toApiError(err)
  }
}

/**
 * Получение пары JWT. Для кастомного User с USERNAME_FIELD=email
 * сериализатор SimpleJWT ожидает поле `email`, а не `username`.
 */
export async function obtainTokenPair(email: string, password: string): Promise<TokenPair> {
  try {
    const res = await plainClient.post<TokenPair>('/token/', { email, password })
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function fetchCurrentUser(): Promise<UserProfile> {
  try {
    const res = await http.get<UserProfile>('/v1/users/me/')
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export function attachTokensToClient(tokens: TokenPair) {
  setAuthTokens(tokens.access, tokens.refresh)
}
