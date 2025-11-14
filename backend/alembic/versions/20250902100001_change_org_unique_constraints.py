"""Change organization unique constraints to composite

Revision ID: 2025090210001
Revises: 8275d5d05e2c4110
Create Date: 2025-09-02 10:00:01.000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250902100001"
down_revision: Union[str, None] = "8275d5d05e2c4110"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing individual unique constraints
    op.drop_constraint("organizations_name_key", "organizations", type_="unique")
    op.drop_constraint("organizations_slug_key", "organizations", type_="unique")

    # Add a composite unique constraint on name and slug together
    op.create_unique_constraint(
        "organizations_name_slug_key", "organizations", ["name", "slug"]
    )


def downgrade() -> None:
    # Drop the composite unique constraint
    op.drop_constraint("organizations_name_slug_key", "organizations", type_="unique")

    # Restore the individual unique constraints
    op.create_unique_constraint("organizations_name_key", "organizations", ["name"])
    op.create_unique_constraint("organizations_slug_key", "organizations", ["slug"])
