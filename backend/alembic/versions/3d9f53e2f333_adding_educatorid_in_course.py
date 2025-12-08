"""adding educatorid in course"""

# revision identifiers, used by Alembic.
revision = '3d9f53e2f333'
down_revision = '07bdcadb6e6a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column(
        'courses',
        sa.Column('educator_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_courses_educator', 'courses', 'users',
        ['educator_id'], ['id']
    )
    # Optional: set a default educator on existing rows
    op.execute("UPDATE courses SET educator_id = 1 WHERE educator_id IS NULL")
    op.alter_column('courses', 'educator_id', nullable=False)

def downgrade():
    op.drop_constraint('fk_courses_educator', 'courses', type_='foreignkey')
    op.drop_column('courses', 'educator_id')
