// services/rbac-service.ts
import { apiClient } from '@/lib/api/client';

// Import types from centralized location
import type {
  Role,
  Permission,
  RolePermission,
  UserRole,
  RoleWithPermissions
} from '@/types/rbac';

// RBAC Service class
class RBACService {
  private baseUrl = '/api/v1/rbac';

  // Role operations
  async createRole(roleData: Omit<Role, 'id' | 'is_system_role' | 'created_at' | 'updated_at'>): Promise<Role> {
    const response = await apiClient.post<Role>(`${this.baseUrl}/roles`, roleData);
    return response.data;
  }

  async getRoleById(roleId: string): Promise<Role> {
    const response = await apiClient.get<Role>(`${this.baseUrl}/roles/${roleId}`);
    return response.data;
  }

  async getAllRoles(): Promise<Role[]> {
    const response = await apiClient.get<Role[]>(`${this.baseUrl}/roles`);
    return response.data;
  }

  async updateRole(roleId: string, roleData: Partial<Omit<Role, 'id' | 'is_system_role' | 'created_at' | 'updated_at'>>): Promise<Role> {
    const response = await apiClient.put<Role>(`${this.baseUrl}/roles/${roleId}`, roleData);
    return response.data;
  }

  async deleteRole(roleId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/roles/${roleId}`);
  }

  // Permission operations
  async createPermission(permissionData: Omit<Permission, 'id' | 'created_at' | 'updated_at'>): Promise<Permission> {
    const response = await apiClient.post<Permission>(`${this.baseUrl}/permissions`, permissionData);
    return response.data;
  }

  async getPermissionById(permissionId: string): Promise<Permission> {
    const response = await apiClient.get<Permission>(`${this.baseUrl}/permissions/${permissionId}`);
    return response.data;
  }

  async getAllPermissions(): Promise<Permission[]> {
    const response = await apiClient.get<Permission[]>(`${this.baseUrl}/permissions`);
    return response.data;
  }

  async updatePermission(permissionId: string, permissionData: Partial<Omit<Permission, 'id' | 'created_at' | 'updated_at'>>): Promise<Permission> {
    const response = await apiClient.put<Permission>(`${this.baseUrl}/permissions/${permissionId}`, permissionData);
    return response.data;
  }

  async deletePermission(permissionId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/permissions/${permissionId}`);
  }

  // Role-Permission operations
  async assignPermissionToRole(roleId: string, permissionId: string): Promise<RolePermission> {
    const response = await apiClient.post<RolePermission>(`${this.baseUrl}/roles/${roleId}/permissions`, {
      permission_id: permissionId,
    });
    return response.data;
  }

  async removePermissionFromRole(roleId: string, permissionId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/roles/${roleId}/permissions/${permissionId}`);
  }

  async getPermissionsForRole(roleId: string): Promise<Permission[]> {
    const response = await apiClient.get<Permission[]>(`${this.baseUrl}/roles/${roleId}/permissions`);
    return response.data;
  }

  // User-Role operations
  async assignRoleToUser(userRoleData: Omit<UserRole, 'id' | 'created_at' | 'updated_at'>): Promise<UserRole> {
    const response = await apiClient.post<UserRole>(`${this.baseUrl}/user-roles`, userRoleData);
    return response.data;
  }

  async updateUserRole(userRoleId: string, userRoleData: Partial<Omit<UserRole, 'id' | 'user_id' | 'created_at' | 'updated_at'>>): Promise<UserRole> {
    const response = await apiClient.put<UserRole>(`${this.baseUrl}/user-roles/${userRoleId}`, userRoleData);
    return response.data;
  }

  async removeRoleFromUser(userRoleId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/user-roles/${userRoleId}`);
  }

  async getRolesForUser(userId: string, organizationId?: string): Promise<Role[]> {
    const endpoint = organizationId
      ? `${this.baseUrl}/users/${userId}/roles?organization_id=${organizationId}`
      : `${this.baseUrl}/users/${userId}/roles`;
    const response = await apiClient.get<Role[]>(endpoint);
    return response.data;
  }

  async getUserRolesWithPermissions(userId: string, organizationId?: string): Promise<RoleWithPermissions[]> {
    const endpoint = organizationId
      ? `${this.baseUrl}/users/${userId}/roles-with-permissions?organization_id=${organizationId}`
      : `${this.baseUrl}/users/${userId}/roles-with-permissions`;
    const response = await apiClient.get<RoleWithPermissions[]>(endpoint);
    return response.data;
  }

  async userHasPermission(userId: string, permissionName: string, organizationId?: string): Promise<boolean> {
    const params = new URLSearchParams({ permission_name: permissionName });
    if (organizationId) params.append('organization_id', organizationId);
    const response = await apiClient.get<{ has_permission: boolean }>(`${this.baseUrl}/users/${userId}/has-permission?${params}`);
    return response.data.has_permission;
  }

  async userHasRole(userId: string, roleName: string, organizationId?: string): Promise<boolean> {
    const params = new URLSearchParams({ role_name: roleName });
    if (organizationId) params.append('organization_id', organizationId);
    const response = await apiClient.get<{ has_role: boolean }>(`${this.baseUrl}/users/${userId}/has-role?${params}`);
    return response.data.has_role;
  }
}

// Export singleton instance
export const rbacService = new RBACService();
