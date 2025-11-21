# Frontend Services

This directory contains service classes for making API calls to the backend. Each service handles a specific domain area and provides a clean, typed interface for frontend components.

## Available Services

### AuthService (`auth-service.ts`)
Handles authentication-related API calls to the backend.

**Methods:**
- `processInvitation(token, userId)` - Process an invitation to add a user to an organization
- `getCurrentUser()` - Get the current user profile
- `refreshToken(refreshToken)` - Refresh an auth token
- `signOut()` - Sign out and invalidate session

**Example Usage:**
```typescript
import { authService } from '@/services/auth-service';

// Process an invitation
const result = await authService.processInvitation(token, userId);
if (result.success) {
  console.log('User added to organization:', result.data);
} else {
  console.error('Failed to process invitation:', result.error);
}
```

### OrganizationService (`organization-service.ts`)
Handles organization-related API calls.

**Methods:**
- `createOrganization(data)` - Create a new organization
- `getOrganization(id)` - Get organization details
- `updateOrganization(id, data)` - Update organization
- `deleteOrganization(id)` - Delete organization
- `inviteMember(data)` - Invite a member to organization
- And more...

### BillingService (`billing-service.ts`)
Handles billing and subscription-related API calls.

**Methods:**
- `createCheckoutSession(data)` - Create Stripe checkout session
- `createPortalSession(data)` - Create billing portal session
- `getSubscription()` - Get current subscription
- And more...

### RBACService (`rbac-service.ts`)
Handles role-based access control API calls.

**Methods:**
- `getRoles()` - Get all roles
- `getPermissions()` - Get all permissions
- `assignRole(data)` - Assign role to user
- `removeRole(data)` - Remove role from user
- And more...

## Service Architecture

Each service follows a consistent pattern:

1. **Environment Configuration**: Uses `NEXT_PUBLIC_API_URL` for backend API URL
2. **Authentication**: Automatically includes Supabase auth token in requests
3. **OpenTelemetry Tracing**: Integrated tracing for monitoring and debugging
4. **Error Handling**: Consistent error response format
5. **Type Safety**: Full TypeScript support with proper types

## Adding a New Service

To add a new service:

1. Create a new file in `/services` directory
2. Follow the pattern of existing services
3. Include:
   - Base URL configuration
   - `getAccessToken()` method
   - `fetchWithAuth()` wrapper
   - Individual API methods
4. Export a singleton instance
5. Import and use in components/contexts

## Best Practices

- Always use the service methods instead of direct `fetch()` calls
- Handle success/error responses appropriately
- Use the tracing for debugging and monitoring
- Keep service methods focused on single responsibilities
