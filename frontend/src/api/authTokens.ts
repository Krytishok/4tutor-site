let accessToken: string | null = null
let refreshToken: string | null = null

let onAccessRefreshed: ((access: string) => void) | null = null

export function setOnAccessRefreshed(handler: ((access: string) => void) | null) {
  onAccessRefreshed = handler
}

export function getAccessToken(): string | null {
  return accessToken
}

export function getRefreshToken(): string | null {
  return refreshToken
}

export function setAuthTokens(access: string | null, refresh: string | null) {
  accessToken = access
  refreshToken = refresh
}

export function setAccessTokenOnly(access: string) {
  accessToken = access
}

export function clearAuthTokens() {
  accessToken = null
  refreshToken = null
}

export function notifyAccessRefreshed(access: string) {
  onAccessRefreshed?.(access)
}
