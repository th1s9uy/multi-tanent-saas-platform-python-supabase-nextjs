"""Add email verification tokens table

Revision ID: d1e2f3g4h5i6
Revises: c1d2e3f4g5h6
Create Date: 2025-10-04 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Email Verification Tokens table
    op.create_table('email_verification_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False, comment='Reference to auth.users.id'),
        sa.Column('token', sa.VARCHAR(length=255), nullable=False, comment='Verification token'),
        sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('used_at', postgresql.TIMESTAMP(timezone=True), nullable=True, comment='When token was used'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
        sa.UniqueConstraint('user_id', name='uq_email_verification_tokens_user_id')  # One token per user
    )

    # Create indexes
    op.create_index('idx_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
    op.create_index('idx_email_verification_tokens_token', 'email_verification_tokens', ['token'])
    op.create_index('idx_email_verification_tokens_expires_at', 'email_verification_tokens', ['expires_at'])

    # Enable RLS on email_verification_tokens table
    op.execute("ALTER TABLE email_verification_tokens ENABLE ROW LEVEL SECURITY")

    # Create policy for email_verification_tokens - users can only access their own tokens
    op.execute("""
        CREATE POLICY "Users can view own email verification tokens"
        ON email_verification_tokens FOR SELECT
        TO authenticated
        USING (user_id = auth.uid())
    """)

    op.execute("""
        CREATE POLICY "Users can insert own email verification tokens"
        ON email_verification_tokens FOR INSERT
        TO authenticated
        WITH CHECK (user_id = auth.uid())
    """)

    op.execute("""
        CREATE POLICY "Users can update own email verification tokens"
        ON email_verification_tokens FOR UPDATE
        TO authenticated
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid())
    """)

    op.execute("""
        CREATE POLICY "Users can delete own email verification tokens"
        ON email_verification_tokens FOR DELETE
        TO authenticated
        USING (user_id = auth.uid())
    """)


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS "Users can delete own email verification tokens" ON email_verification_tokens')
    op.execute('DROP POLICY IF EXISTS "Users can update own email verification tokens" ON email_verification_tokens')
    op.execute('DROP POLICY IF EXISTS "Users can insert own email verification tokens" ON email_verification_tokens')
    op.execute('DROP POLICY IF EXISTS "Users can view own email verification tokens" ON email_verification_tokens')

    # Disable RLS on email_verification_tokens table
    op.execute("ALTER TABLE email_verification_tokens DISABLE ROW LEVEL SECURITY")

    # Drop indexes
    op.drop_index('idx_email_verification_tokens_expires_at')
    op.drop_index('idx_email_verification_tokens_token')
    op.drop_index('idx_email_verification_tokens_user_id')

    # Drop table
    op.drop_table('email_verification_tokens')