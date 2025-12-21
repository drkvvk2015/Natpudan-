import apiClient from './apiClient'

export interface UserOut {
  id: number
  email: string
  full_name: string
  role: 'staff' | 'doctor' | 'admin'
  is_active: boolean
  license_number?: string | null
}

export interface CreateUserPayload {
  email: string
  password: string
  full_name: string
  role?: 'staff' | 'doctor' | 'admin'
  license_number?: string
  is_active?: boolean
}

export interface UpdateUserPayload {
  full_name?: string
  role?: 'staff' | 'doctor' | 'admin'
  license_number?: string
  is_active?: boolean
}

export async function listUsers(q?: string): Promise<UserOut[]> {
  const params: any = {}
  if (q) params.q = q
  const res = await apiClient.get<UserOut[]>('/api/admin/users', { params })
  return res.data
}

export async function createUser(payload: CreateUserPayload): Promise<UserOut> {
  const res = await apiClient.post<UserOut>('/api/admin/users', payload)
  return res.data
}

export async function updateUser(id: number, payload: UpdateUserPayload): Promise<UserOut> {
  const res = await apiClient.put<UserOut>(`/api/admin/users/${id}`, payload)
  return res.data
}

export async function setPassword(id: number, password: string): Promise<void> {
  await apiClient.patch(`/api/admin/users/${id}/password`, { password })
}

export async function deleteUser(id: number): Promise<void> {
  await apiClient.delete(`/api/admin/users/${id}`)
}
