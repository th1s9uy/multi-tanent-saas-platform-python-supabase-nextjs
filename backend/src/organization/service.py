"""
Organization service for managing organizations in a multi-tenant SaaS platform.
"""

import logging
import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from opentelemetry import trace, metrics
from config import supabase_config
from src.organization.models import Organization, OrganizationCreate, OrganizationUpdate
from src.organization.invitation_models import Invitation, InvitationCreate, InvitationStatus
from src.common.errors import ErrorCode
from src.notifications.service import notification_service
from src.notifications.models import SendNotificationRequest
from src.rbac.roles.service import role_service
from src.rbac.user_roles.service import user_role_service
from src.rbac.user_roles.models import UserRoleCreate

logger = logging.getLogger(__name__)

# Get tracer for this module
tracer = trace.get_tracer(__name__)

# Get meter for this module
meter = metrics.get_meter(__name__)

# Create metrics
organization_operations_counter = meter.create_counter(
    "organization.operations",
    description="Number of organization operations"
)

organization_errors_counter = meter.create_counter(
    "organization.errors",
    description="Number of organization operation errors"
)


class OrganizationService:
    """Service for handling organization operations."""
    
    def __init__(self):
        self.supabase_config = supabase_config
    
    @property
    def supabase(self):
        """Get Supabase client, raise error if not configured."""
        if not self.supabase_config.is_configured():
            logger.error("Supabase is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
            raise ValueError("Supabase is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
        return self.supabase_config.client
    
    @tracer.start_as_current_span("organization.create_organization")
    async def create_organization(self, org_data: OrganizationCreate) -> tuple[Optional[Organization], Optional[str]]:
        """Create a new organization."""
        organization_operations_counter.add(1, {"operation": "create_organization"})
        
        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("organization.name", org_data.name)
        try:
            response = self.supabase.table("organizations").insert({
                "name": org_data.name,
                "description": org_data.description,
                "slug": org_data.slug,
                "is_active": org_data.is_active
            }).execute()
            
            if not response.data:
                logger.error(f"Failed to create organization: {org_data.name}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Failed to create organization"))
                organization_errors_counter.add(1, {"operation": "create_organization", "error": "no_data_returned"})
                return None, "Failed to create organization"
            
            org_dict = response.data[0]
            organization = Organization(
                id=org_dict["id"],
                name=org_dict["name"],
                description=org_dict["description"],
                slug=org_dict["slug"],
                is_active=org_dict["is_active"],
                created_at=org_dict["created_at"],
                updated_at=org_dict["updated_at"]
            )
            current_span.set_attribute("organization.id", str(organization.id))
            current_span.set_status(trace.Status(trace.StatusCode.OK))
            return organization, None
            
        except Exception as e:
            logger.error(f"Exception while creating organization '{org_data.name}': {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "create_organization", "error": "exception"})
            return None, str(e)
    
    @tracer.start_as_current_span("organization.get_organization_by_id")
    async def get_organization_by_id(self, org_id: UUID) -> tuple[Optional[Organization], Optional[str]]:
        """Get an organization by its ID."""
        organization_operations_counter.add(1, {"operation": "get_organization_by_id"})
        
        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("organization.id", str(org_id))
        try:
            response = self.supabase.table("organizations").select("*").eq("id", str(org_id)).execute()
            
            if not response.data:
                logger.warning(f"Organization not found: {org_id}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Organization not found"))
                organization_errors_counter.add(1, {"operation": "get_organization_by_id", "error": "not_found"})
                return None, "Organization not found"
            
            org_dict = response.data[0]
            organization = Organization(
                id=org_dict["id"],
                name=org_dict["name"],
                description=org_dict["description"],
                slug=org_dict["slug"],
                is_active=org_dict["is_active"],
                created_at=org_dict["created_at"],
                updated_at=org_dict["updated_at"]
            )
            current_span.set_status(trace.Status(trace.StatusCode.OK))
            return organization, None
            
        except Exception as e:
            logger.error(f"Exception while getting organization {org_id}: {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "get_organization_by_id", "error": "exception"})
            return None, str(e)
    
    @tracer.start_as_current_span("organization.get_organization_by_slug")
    async def get_organization_by_slug(self, slug: str) -> tuple[Optional[Organization], Optional[str]]:
        """Get an organization by its slug."""
        organization_operations_counter.add(1, {"operation": "get_organization_by_slug"})
        
        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("organization.slug", slug)
        try:
            response = self.supabase.table("organizations").select("*").eq("slug", slug).execute()
            
            if not response.data:
                logger.warning(f"Organization not found with slug: {slug}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Organization not found"))
                organization_errors_counter.add(1, {"operation": "get_organization_by_slug", "error": "not_found"})
                return None, "Organization not found"
            
            org_dict = response.data[0]
            organization = Organization(
                id=org_dict["id"],
                name=org_dict["name"],
                description=org_dict["description"],
                slug=org_dict["slug"],
                is_active=org_dict["is_active"],
                created_at=org_dict["created_at"],
                updated_at=org_dict["updated_at"]
            )
            current_span.set_status(trace.Status(trace.StatusCode.OK))
            return organization, None
            
        except Exception as e:
            logger.error(f"Exception while getting organization with slug '{slug}': {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "get_organization_by_slug", "error": "exception"})
            return None, str(e)
    
    @tracer.start_as_current_span("organization.get_all_organizations")
    async def get_all_organizations(self) -> tuple[list[Organization], Optional[str]]:
        """Get all organizations."""
        organization_operations_counter.add(1, {"operation": "get_all_organizations"})
        
        try:
            response = self.supabase.table("organizations").select("*").execute()
            
            organizations = []
            for org_dict in response.data:
                organizations.append(Organization(
                    id=org_dict["id"],
                    name=org_dict["name"],
                    description=org_dict["description"],
                    slug=org_dict["slug"],
                    is_active=org_dict["is_active"],
                    created_at=org_dict["created_at"],
                    updated_at=org_dict["updated_at"]
                ))
            
            return organizations, None
            
        except Exception as e:
            logger.error(f"Exception while getting all organizations: {e}", exc_info=True)
            organization_errors_counter.add(1, {"operation": "get_all_organizations", "error": "exception"})
            return [], str(e)
    
    @tracer.start_as_current_span("organization.update_organization")
    async def update_organization(self, org_id: UUID, org_data: OrganizationUpdate) -> tuple[Optional[Organization], Optional[str]]:
        """Update an organization."""
        organization_operations_counter.add(1, {"operation": "update_organization"})
        
        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("organization.id", str(org_id))
        try:
            update_data = {}
            if org_data.name is not None:
                update_data["name"] = org_data.name
                current_span.set_attribute("organization.name.updated", True)
            if org_data.description is not None:
                update_data["description"] = org_data.description
            if org_data.slug is not None:
                update_data["slug"] = org_data.slug
                current_span.set_attribute("organization.slug.updated", True)
            if org_data.is_active is not None:
                update_data["is_active"] = org_data.is_active
            
            if not update_data:
                return await self.get_organization_by_id(org_id)
            
            response = self.supabase.table("organizations").update(update_data).eq("id", str(org_id)).execute()
            
            if not response.data:
                logger.error(f"Organization not found or update failed: {org_id}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Organization not found or update failed"))
                organization_errors_counter.add(1, {"operation": "update_organization", "error": "not_found_or_failed"})
                return None, "Organization not found or update failed"
            
            org_dict = response.data[0]
            organization = Organization(
                id=org_dict["id"],
                name=org_dict["name"],
                description=org_dict["description"],
                slug=org_dict["slug"],
                is_active=org_dict["is_active"],
                created_at=org_dict["created_at"],
                updated_at=org_dict["updated_at"]
            )
            current_span.set_status(trace.Status(trace.StatusCode.OK))
            return organization, None
            
        except Exception as e:
            logger.error(f"Exception while updating organization {org_id}: {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "update_organization", "error": "exception"})
            return None, str(e)
    
    @tracer.start_as_current_span("organization.delete_organization")
    async def delete_organization(self, org_id: UUID) -> tuple[bool, Optional[str]]:
        """Delete an organization."""
        organization_operations_counter.add(1, {"operation": "delete_organization"})

        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("organization.id", str(org_id))
        try:
            response = self.supabase.table("organizations").delete().eq("id", str(org_id)).execute()

            if not response.data:
                logger.warning(f"Organization not found for deletion: {org_id}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Organization not found"))
                organization_errors_counter.add(1, {"operation": "delete_organization", "error": "not_found"})
                return False, "Organization not found"

            current_span.set_status(trace.Status(trace.StatusCode.OK))
            return True, None

        except Exception as e:
            logger.error(f"Exception while deleting organization {org_id}: {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "delete_organization", "error": "exception"})
            return False, str(e)

    @tracer.start_as_current_span("organization.create_invitation")
    async def create_invitation(self, invite_data: InvitationCreate) -> tuple[Optional[Invitation], Optional[str]]:
        """Create a new invitation for an organization member."""
        organization_operations_counter.add(1, {"operation": "create_invitation"})

        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("invitation.email", invite_data.email)
        current_span.set_attribute("organization.id", str(invite_data.organization_id))

        try:
            # Check if user already exists with this email
            from src.auth.service import auth_service
            existing_user, error = await auth_service.get_user_by_email(invite_data.email)

            # Handle error from get_user_by_email
            if error:
                logger.error(f"Failed to check if user exists: {error}")
                return None, "Failed to check user existence"

            if existing_user:
                # User exists - check if they're already a member of this organization
                current_span.add_event("user_exists", {"user_id": str(existing_user.id)})
                logger.info(f"User {invite_data.email} already exists - checking organization membership")

                # Cancel any existing pending invitations for this email and organization
                logger.info(f"Cancelling any existing pending invitations for {invite_data.email} in organization {invite_data.organization_id}")
                cancel_response = self.supabase.table("invitations").update({
                    "status": InvitationStatus.CANCELLED.value
                }).eq("email", invite_data.email).eq("organization_id", str(invite_data.organization_id)).eq("status", InvitationStatus.PENDING.value).execute()

                if cancel_response.data:
                    logger.info(f"Cancelled {len(cancel_response.data)} existing pending invitation(s) for {invite_data.email}")

                # Check if user is already a member of this organization
                user_roles, membership_error = await user_role_service.get_user_roles(
                    existing_user.id,
                    invite_data.organization_id
                )

                if membership_error:
                    logger.error(f"Failed to check user membership: {membership_error}")
                    return None, "Failed to check user membership"

                if user_roles and len(user_roles) > 0:
                    # User is already a member - return error without sending any email
                    logger.info(f"User {invite_data.email} is already a member of organization {invite_data.organization_id}")

                    current_span.set_attribute("user.id", str(existing_user.id))
                    current_span.set_attribute("invitation.status", "already_member")
                    current_span.set_status(trace.Status(trace.StatusCode.OK))

                    # Return error code instead of string message
                    return None, ErrorCode.USER_ALREADY_MEMBER.value

                # User is not a member - add them to the organization
                current_span.add_event("adding_existing_user", {"user_id": str(existing_user.id)})
                logger.info(f"User {invite_data.email} is not a member - adding to organization")

                # Get the regular_user role
                member_role, role_error = await role_service.get_role_by_name("regular_user")
                if role_error or not member_role:
                    logger.error(f"Could not find 'regular_user' role: {role_error}")
                    return None, "Role not found"

                # Add user to organization
                user_role_data = UserRoleCreate(
                    user_id=existing_user.id,
                    role_id=member_role.id,
                    organization_id=invite_data.organization_id
                )

                user_role, role_assign_error = await user_role_service.assign_role_to_user(user_role_data)
                if role_assign_error or not user_role:
                    logger.error(f"Failed to assign role to user: {role_assign_error}")
                    return None, "Failed to assign role to user"

                # Create a virtual invitation record for tracking
                token = secrets.token_urlsafe(32)
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                invitation_dict = {
                    "id": secrets.token_urlsafe(16),  # Temporary ID
                    "email": invite_data.email,
                    "organization_id": str(invite_data.organization_id),
                    "invited_by": str(invite_data.invited_by),
                    "token": token,
                    "status": InvitationStatus.ACCEPTED.value,
                    "expires_at": expires_at.isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "accepted_at": datetime.now(timezone.utc).isoformat()
                }

                invitation = Invitation(
                    id=invitation_dict["id"],
                    email=invitation_dict["email"],
                    organization_id=invitation_dict["organization_id"],
                    invited_by=invitation_dict["invited_by"],
                    token=invitation_dict["token"],
                    status=InvitationStatus.ACCEPTED,
                    expires_at=invitation_dict["expires_at"],
                    created_at=invitation_dict["created_at"],
                    accepted_at=invitation_dict["accepted_at"]
                )

                current_span.set_attribute("user.id", str(existing_user.id))
                current_span.set_attribute("invitation.type", "direct_addition")

                # Send notification email
                try:
                    # Get the organization name
                    org, org_error = await self.get_organization_by_id(invite_data.organization_id)
                    if org_error or not org:
                        logger.warning(f"Could not fetch organization name: {org_error}")

                    # Create notification request
                    notification_request = SendNotificationRequest(
                        event_key="organization.invitation",
                        recipient_email=invite_data.email,
                        recipient_name=f"{existing_user.first_name} {existing_user.last_name}",
                        organization_id=invite_data.organization_id,
                        user_id=existing_user.id,
                        template_variables={
                            "recipient_name": f"{existing_user.first_name} {existing_user.last_name}",
                            "inviter_name": "An administrator",
                            "organization_name": org.name if org else "the organization",
                            "role_name": "Member",
                            "invitation_url": f"{self._get_frontend_url()}/auth/signin",
                            "expiry_days": "7",
                            "app_name": "Your Platform"
                        }
                    )

                    # Send the notification
                    await notification_service.send_notification(notification_request)

                    logger.info(f"Member added notification sent to {invite_data.email}")
                except Exception as email_error:
                    logger.error(f"Failed to send notification email: {email_error}", exc_info=True)
                    # Don't fail the operation if email sending fails
                    current_span.add_event("email_send_failed", {"error": str(email_error)})

                current_span.set_status(trace.Status(trace.StatusCode.OK))
                return invitation, None
            else:
                # User doesn't exist - create invitation token and send signup email
                current_span.add_event("user_not_exists", {"action": "create_invitation"})
                logger.info(f"User {invite_data.email} doesn't exist - creating invitation")

                # Cancel any existing pending invitations for this email and organization
                logger.info(f"Cancelling any existing pending invitations for {invite_data.email} in organization {invite_data.organization_id}")
                cancel_response = self.supabase.table("invitations").update({
                    "status": InvitationStatus.CANCELLED.value
                }).eq("email", invite_data.email).eq("organization_id", str(invite_data.organization_id)).eq("status", InvitationStatus.PENDING.value).execute()

                if cancel_response.data:
                    logger.info(f"Cancelled {len(cancel_response.data)} existing pending invitation(s) for {invite_data.email}")

                # Generate a unique invitation token
                token = secrets.token_urlsafe(32)
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Invitation expires in 7 days

                # Insert the invitation into the database
                response = self.supabase.table("invitations").insert({
                    "email": invite_data.email,
                    "organization_id": str(invite_data.organization_id),
                    "invited_by": str(invite_data.invited_by),
                    "token": token,
                    "status": InvitationStatus.PENDING.value,
                    "expires_at": expires_at.isoformat()
                }).execute()

                if not response.data:
                    logger.error(f"Failed to create invitation for {invite_data.email}")
                    current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Failed to create invitation"))
                    organization_errors_counter.add(1, {"operation": "create_invitation", "error": "no_data_returned"})
                    return None, "Failed to create invitation"

                invitation_dict = response.data[0]
                invitation = Invitation(
                    id=invitation_dict["id"],
                    email=invitation_dict["email"],
                    organization_id=invitation_dict["organization_id"],
                    invited_by=invitation_dict["invited_by"],
                    token=invitation_dict["token"],
                    status=InvitationStatus(invitation_dict["status"]),
                    expires_at=invitation_dict["expires_at"],
                    created_at=invitation_dict["created_at"],
                    accepted_at=invitation_dict.get("accepted_at")
                )

                current_span.set_attribute("invitation.id", str(invitation.id))
                current_span.set_attribute("invitation.type", "signup_invitation")

                # Send the invitation email
                try:
                    # Get the organization name
                    org, org_error = await self.get_organization_by_id(invite_data.organization_id)
                    if org_error or not org:
                        logger.warning(f"Could not fetch organization name for invitation: {org_error}")

                    # Create notification request
                    notification_request = SendNotificationRequest(
                        event_key="organization.invitation",
                        recipient_email=invite_data.email,
                        organization_id=invite_data.organization_id,
                        template_variables={
                            "recipient_name": "there",  # Generic greeting since we don't know their name yet
                            "inviter_name": "An administrator",
                            "organization_name": org.name if org else "the organization",
                            "role_name": "Member",
                            "invitation_url": f"{self._get_frontend_url()}/auth/signup?token={token}",
                            "expiry_days": "7",
                            "app_name": "Your Platform"
                        }
                    )

                    # Send the notification
                    await notification_service.send_notification(notification_request)

                    logger.info(f"Invitation email sent to {invite_data.email}")
                except Exception as email_error:
                    logger.error(f"Failed to send invitation email: {email_error}", exc_info=True)
                    # Don't fail the invitation creation if email sending fails
                    current_span.add_event("email_send_failed", {"error": str(email_error)})

                current_span.set_status(trace.Status(trace.StatusCode.OK))
                return invitation, None

        except Exception as e:
            logger.error(f"Exception while creating invitation: {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "create_invitation", "error": "exception"})
            return None, str(e)

    def _get_frontend_url(self) -> str:
        """Get the frontend URL from environment variables."""
        from config.settings import settings
        return settings.app_base_url or "http://localhost:3000"

    @tracer.start_as_current_span("organization.process_invitation")
    async def process_invitation(self, token: str, user_id: UUID) -> tuple[Optional[Invitation], Optional[str]]:
        """Process an invitation after user signup."""
        organization_operations_counter.add(1, {"operation": "process_invitation"})

        # Set attribute on current span
        current_span = trace.get_current_span()
        current_span.set_attribute("invitation.token", token[:8] + "...")
        current_span.set_attribute("user.id", str(user_id))

        try:
            from datetime import datetime

            # Get the invitation by token
            response = self.supabase.table("invitations").select("*").eq("token", token).execute()

            if not response.data:
                logger.warning(f"Invitation not found with token: {token[:8]}...")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Invitation not found"))
                organization_errors_counter.add(1, {"operation": "process_invitation", "error": "not_found"})
                return None, "Invitation not found"

            invitation_dict = response.data[0]

            # Check if invitation is already accepted
            if invitation_dict["status"] == InvitationStatus.ACCEPTED.value:
                logger.warning(f"Invitation already accepted: {token[:8]}...")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Invitation already accepted"))
                return None, "Invitation already accepted"

            # Check if invitation is expired
            expires_at = datetime.fromisoformat(invitation_dict["expires_at"].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expires_at:
                # Update status to expired
                self.supabase.table("invitations").update({
                    "status": InvitationStatus.EXPIRED.value
                }).eq("id", invitation_dict["id"]).execute()

                logger.warning(f"Invitation expired: {token[:8]}...")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Invitation expired"))
                return None, "Invitation has expired"

            # Get the organization
            org, org_error = await self.get_organization_by_id(UUID(invitation_dict["organization_id"]))
            if org_error or not org:
                logger.error(f"Organization not found for invitation: {invitation_dict['organization_id']}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Organization not found"))
                return None, "Organization not found"

            # Get the default regular_user role
            member_role, role_error = await role_service.get_role_by_name("regular_user")
            if role_error or not member_role:
                logger.error(f"Could not find 'regular_user' role: {role_error}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Role not found"))
                return None, "Role not found"

            # Add user to organization
            user_role_data = UserRoleCreate(
                user_id=user_id,
                role_id=member_role.id,
                organization_id=org.id
            )

            user_role, role_assign_error = await user_role_service.assign_role_to_user(user_role_data)
            if role_assign_error or not user_role:
                logger.error(f"Failed to assign role to user: {role_assign_error}")
                current_span.set_status(trace.Status(trace.StatusCode.ERROR, "Failed to assign role"))
                return None, "Failed to assign role to user"

            # Update invitation status to accepted
            self.supabase.table("invitations").update({
                "status": InvitationStatus.ACCEPTED.value,
                "accepted_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", invitation_dict["id"]).execute()

            # Create Invitation object to return
            invitation = Invitation(
                id=invitation_dict["id"],
                email=invitation_dict["email"],
                organization_id=invitation_dict["organization_id"],
                invited_by=invitation_dict["invited_by"],
                token=invitation_dict["token"],
                status=InvitationStatus.ACCEPTED,
                expires_at=invitation_dict["expires_at"],
                created_at=invitation_dict["created_at"],
                accepted_at=datetime.now(timezone.utc)
            )

            current_span.set_attribute("organization.id", str(org.id))
            current_span.set_status(trace.Status(trace.StatusCode.OK))

            logger.info(f"User {user_id} successfully joined organization {org.id} via invitation")
            return invitation, None

        except Exception as e:
            logger.error(f"Exception while processing invitation: {e}", exc_info=True)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            organization_errors_counter.add(1, {"operation": "process_invitation", "error": "exception"})
            return None, str(e)


# Global organization service instance
organization_service = OrganizationService()