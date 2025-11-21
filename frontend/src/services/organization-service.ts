// services/organization-service.ts
import { apiClient } from '@/lib/api/client';

// Import types from centralized location
import type { Organization, OrganizationCreate, OrganizationUpdate, Invitation } from '@/types/organization';
import type { Member } from '@/types/user';

// Organization Service class
class OrganizationService {

  private baseUrl = '/api/v1/organizations';

  // Create organization for current user using the self endpoint
  async createSelfOrganization(orgData: OrganizationCreate): Promise<Organization> {
    const response = await apiClient.post<Organization>(`${this.baseUrl}/self`, orgData);
    return response.data;
  }

  // Get organizations for current user
  async getUserOrganizations(): Promise<Organization[]> {
    const response = await apiClient.get<Organization[]>(this.baseUrl);
    return response.data;
  }

  // Create organization (platform admin only)
  async createOrganization(orgData: OrganizationCreate): Promise<Organization> {
    const response = await apiClient.post<Organization>(this.baseUrl, orgData);
    return response.data;
  }

  // Update organization
  async updateOrganization(orgId: string, orgData: OrganizationUpdate): Promise<Organization> {
    const response = await apiClient.put<Organization>(`${this.baseUrl}/${orgId}`, orgData);
    return response.data;
  }

  // Delete organization
  async deleteOrganization(orgId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${orgId}`);
  }

  // Get organization by ID
  async getOrganizationById(orgId: string): Promise<Organization> {
    const response = await apiClient.get<Organization>(`${this.baseUrl}/${orgId}`);
    return response.data;
  }

  // Get organization members
  async getOrganizationMembers(orgId: string): Promise<Member[]> {
    const response = await apiClient.get<Member[]>(`${this.baseUrl}/${orgId}/members`);
    return response.data;
  }

  // Invite a member to the organization
  async inviteMember(orgId: string, email: string): Promise<Invitation> {
    const response = await apiClient.post<Invitation>(`${this.baseUrl}/${orgId}/invite`, {
      email,
      organization_id: orgId,
    });
    return response.data;
  }
}

// Export a singleton instance of the Organization service
export const organizationService = new OrganizationService();
