"""
Common error codes for the application.
"""

from enum import Enum


class ErrorCode(Enum):
    """Error codes for consistent error handling."""

    # User/Auth errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_MEMBER = "USER_ALREADY_MEMBER"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # Organization errors
    ORGANIZATION_NOT_FOUND = "ORGANIZATION_NOT_FOUND"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Invitation errors
    INVITATION_EXPIRED = "INVITATION_EXPIRED"
    INVITATION_ALREADY_ACCEPTED = "INVITATION_ALREADY_ACCEPTED"

    # Generic errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
