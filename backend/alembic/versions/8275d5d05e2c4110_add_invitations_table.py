"""Add invitations table

Revision ID: 8275d5d05e2c4110
Revises: d1e2f3g4h5i6
Create Date: 2025-10-29 18:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8275d5d05e2c4110'
down_revision: Union[str, None] = 'd1e2f3g4h5i6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the invitations table with RLS."""
    # Invitations table for organization membership invitations
    op.create_table('invitations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique invitation ID'),
        sa.Column('email', sa.TEXT(), nullable=False, comment='Email address of the invited user'),
        sa.Column('organization_id', sa.UUID(), nullable=False, comment='Organization ID'),
        sa.Column('invited_by', sa.UUID(), nullable=False, comment='User ID who sent the invitation'),
        sa.Column('token', sa.VARCHAR(length=255), nullable=False, comment='Unique invitation token'),
        sa.Column('status', sa.VARCHAR(length=20), nullable=False, server_default='pending', comment='Invitation status (pending, accepted, expired, cancelled)'),
        sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), nullable=False, comment='Invitation expiration time'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Creation timestamp'),
        sa.Column('accepted_at', postgresql.TIMESTAMP(timezone=True), nullable=True, comment='Acceptance timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'expired', 'cancelled')", name='chk_invitation_status'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE', name='fk_invitations_organization_id'),
        sa.ForeignKeyConstraint(['invited_by'], ['auth.users.id'], ondelete='CASCADE', name='fk_invitations_invited_by')
    )

    # Create indexes for better query performance
    op.create_index('idx_invitations_email', 'invitations', ['email'])
    op.create_index('idx_invitations_token', 'invitations', ['token'])
    op.create_index('idx_invitations_organization_id', 'invitations', ['organization_id'])
    op.create_index('idx_invitations_status', 'invitations', ['status'])
    op.create_index('idx_invitations_expires_at', 'invitations', ['expires_at'])

    # Enable RLS on invitations table
    op.execute("ALTER TABLE invitations ENABLE ROW LEVEL SECURITY")

    # Create policy for invitations - organization admins can view all invitations for their organization
    op.execute("""
        CREATE POLICY "Organization admins can view invitations for their organization"
        ON invitations FOR SELECT
        TO authenticated
        USING (
            organization_id IN (
                SELECT organization_id
                FROM user_roles
                JOIN roles ON user_roles.role_id = roles.id
                WHERE user_roles.user_id = auth.uid()
                AND roles.name IN ('org_admin', 'platform_admin')
            )
        )
    """)

    # Create policy for invitations - organization admins can insert invitations for their organization
    op.execute("""
        CREATE POLICY "Organization admins can insert invitations for their organization"
        ON invitations FOR INSERT
        TO authenticated
        WITH CHECK (
            organization_id IN (
                SELECT organization_id
                FROM user_roles
                JOIN roles ON user_roles.role_id = roles.id
                WHERE user_roles.user_id = auth.uid()
                AND roles.name IN ('org_admin', 'platform_admin')
            )
        )
    """)

    # Create policy for invitations - organization admins can update invitations for their organization
    op.execute("""
        CREATE POLICY "Organization admins can update invitations for their organization"
        ON invitations FOR UPDATE
        TO authenticated
        USING (
            organization_id IN (
                SELECT organization_id
                FROM user_roles
                JOIN roles ON user_roles.role_id = roles.id
                WHERE user_roles.user_id = auth.uid()
                AND roles.name IN ('org_admin', 'platform_admin')
            )
        )
        WITH CHECK (
            organization_id IN (
                SELECT organization_id
                FROM user_roles
                JOIN roles ON user_roles.role_id = roles.id
                WHERE user_roles.user_id = auth.uid()
                AND roles.name IN ('org_admin', 'platform_admin')
            )
        )
    """)

    # Create policy for invitations - organization admins can delete invitations for their organization
    op.execute("""
        CREATE POLICY "Organization admins can delete invitations for their organization"
        ON invitations FOR DELETE
        TO authenticated
        USING (
            organization_id IN (
                SELECT organization_id
                FROM user_roles
                JOIN roles ON user_roles.role_id = roles.id
                WHERE user_roles.user_id = auth.uid()
                AND roles.name IN ('org_admin', 'platform_admin')
            )
        )
    """)


def downgrade() -> None:
    """Drop the invitations table."""
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS "Organization admins can delete invitations for their organization" ON invitations')
    op.execute('DROP POLICY IF EXISTS "Organization admins can update invitations for their organization" ON invitations')
    op.execute('DROP POLICY IF EXISTS "Organization admins can insert invitations for their organization" ON invitations')
    op.execute('DROP POLICY IF EXISTS "Organization admins can view invitations for their organization" ON invitations')

    # Disable RLS on invitations table
    op.execute("ALTER TABLE invitations DISABLE ROW LEVEL SECURITY")

    # Drop indexes
    op.drop_index('idx_invitations_expires_at')
    op.drop_index('idx_invitations_status')
    op.drop_index('idx_invitations_organization_id')
    op.drop_index('idx_invitations_token')
    op.drop_index('idx_invitations_email')

    # Drop table
    op.drop_table('invitations')
