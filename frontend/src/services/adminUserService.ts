import apiClient from './apiClient';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'staff' | 'doctor' | 'admin';
  is_active: boolean;
  license_number?: string;
}

export interface CreateUserPayload {
  email: string;
  password: string;
  full_name: string;
  role: 'staff' | 'doctor' | 'admin';
  license_number?: string;
  is_active?: boolean;
}

export interface UpdateUserPayload {
  full_name?: string;
  role?: 'staff' | 'doctor' | 'admin';
  license_number?: string;
  is_active?: boolean;
}

export interface SetPasswordPayload {
  password: string;
}

class AdminUserService {
  /**
   * List all users with optional search and pagination
   */
  async listUsers(skip = 0, limit = 50, search?: string): Promise<User[]> {
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });
      if (search) {
        params.append('q', search);
      }
      const response = await apiClient.get<User[]>(
        `/api/admin/users?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to list users:', error);
      throw error;
    }
  }

  /**
   * Get a single user by ID
   */
  async getUser(userId: number): Promise<User> {
    try {
      const response = await apiClient.get<User>(`/api/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new user
   */
  async createUser(payload: CreateUserPayload): Promise<User> {
    try {
      const response = await apiClient.post<User>(
        '/api/admin/users',
        payload
      );
      return response.data;
    } catch (error) {
      console.error('Failed to create user:', error);
      throw error;
    }
  }

  /**
   * Update a user (full_name, role, license_number, is_active)
   */
  async updateUser(
    userId: number,
    payload: UpdateUserPayload
  ): Promise<User> {
    try {
      const response = await apiClient.put<User>(
        `/api/admin/users/${userId}`,
        payload
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Set or reset a user's password
   */
  async setPassword(
    userId: number,
    payload: SetPasswordPayload
  ): Promise<void> {
    try {
      await apiClient.patch(`/api/admin/users/${userId}/password`, payload);
    } catch (error) {
      console.error(`Failed to set password for user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a user
   */
  async deleteUser(userId: number): Promise<void> {
    try {
      await apiClient.delete(`/api/admin/users/${userId}`);
    } catch (error) {
      console.error(`Failed to delete user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Toggle user active status
   */
  async toggleUserStatus(userId: number, isActive: boolean): Promise<User> {
    return this.updateUser(userId, { is_active: isActive });
  }

  /**
   * Change user role
   */
  async changeUserRole(
    userId: number,
    role: 'staff' | 'doctor' | 'admin'
  ): Promise<User> {
    return this.updateUser(userId, { role });
  }
}

export default new AdminUserService();
