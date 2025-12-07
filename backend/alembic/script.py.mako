"""${message}"""

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${repr(down_revision) if down_revision else "None"}
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    pass

def downgrade():
    pass
