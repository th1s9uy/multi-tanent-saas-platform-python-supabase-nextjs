"""
Pydantic models for Organization Invitation functionality.
"""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class InvitationStatus(str, Enum):
    """Invitation status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class InvitationBase(BaseModel):
    """Base model for Organization Invitation."""
    email: str = Field(..., description="Email address of the invited user")
    organization_id: UUID = Field(..., description="Organization ID")
    invited_by: UUID = Field(..., description="User ID who sent the invitation")


class InvitationCreate(InvitationBase):
    """Model for creating a new invitation."""
    role_id: Optional[UUID] = Field(None, description="Role to assign to the user (optional)")


class InvitationUpdate(BaseModel):
    """Model for updating an invitation."""
    status: Optional[InvitationStatus] = Field(None, description="Invitation status")
    expires_at: Optional[datetime] = Field(None, description="Invitation expiration time")


class Invitation(InvitationBase):
    """Model for an invitation with all attributes."""
    id: UUID = Field(..., description="Invitation ID")
    token: str = Field(..., description="Unique invitation token")
    status: InvitationStatus = Field(..., description="Invitation status")
    expires_at: datetime = Field(..., description="Invitation expiration time")
    created_at: datetime = Field(..., description="Creation timestamp")
    accepted_at: Optional[datetime] = Field(None, description="Acceptance timestamp")

    class Config:
        from_attributes = True
