// services/auth-service.ts
import { apiClient } from '@/lib/api/client';
import type { UserProfile } from '@/types/auth';

// Auth Service class
class AuthService {
  private baseUrl = '/api/v1/auth';

  // Process invitation to add user to organization
  async processInvitation(token: string, userId: string): Promise<{
    success: boolean;
    error?: string;
    data?: unknown;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/process-invitation`, {
        token,
        user_id: userId,
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      const errorMessage = (error as Error).message;
      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // Get current user profile
  async getCurrentUser(): Promise<{
    success: boolean;
    error?: string;
    user?: UserProfile;
  }> {
    try {
      const response = await apiClient.get<UserProfile>(`${this.baseUrl}/me`);

      return {
        success: true,
        user: response.data,
      };
    } catch (error) {
      const errorMessage = (error as Error).message;
      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // Refresh auth token
  async refreshToken(refreshToken: string): Promise<{
    success: boolean;
    error?: string;
    data?: unknown;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/refresh`, {
        refresh_token: refreshToken,
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      const errorMessage = (error as Error).message;
      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // Sign out
  async signOut(): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      await apiClient.post(`${this.baseUrl}/signout`);

      return {
        success: true,
      };
    } catch (error) {
      const errorMessage = (error as Error).message;
      return {
        success: false,
        error: errorMessage,
      };
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
