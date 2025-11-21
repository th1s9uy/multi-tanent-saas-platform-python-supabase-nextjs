import { useQuery } from '@tanstack/react-query';
import { authService } from '@/services/auth-service';
import type { UserRoleAssignment } from '@/types/rbac';

export function useUserProfile(userId?: string) {
  return useQuery({
    queryKey: ['user-profile', userId],
    queryFn: async (): Promise<UserRoleAssignment[]> => {
      const result = await authService.getCurrentUser();

      if (!result.success || !result.user) {
        throw new Error(result.error || 'Failed to fetch user profile');
      }

      // Return just the roles from the full user profile
      return result.user.roles || [];
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (replaces deprecated cacheTime)
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}