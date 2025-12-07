"""autogenerate_test_run"""

# revision identifiers, used by Alembic.
revision = '72cf5bd9d5e8'
down_revision = 'c8915a1ee2e7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
       op.add_column('users', sa.Column('is_ms_account', sa.Boolean(),
                                     server_default=sa.text("false"), nullable=False))

def downgrade():
    pass
