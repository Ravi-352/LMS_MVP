"""autogenerate_test_run"""

# revision identifiers, used by Alembic.
revision = 'fa0be543c584'
down_revision = '72cf5bd9d5e8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.drop_column('users', 'is_ms_account')

def downgrade():
    pass
