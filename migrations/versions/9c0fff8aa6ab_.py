"""empty message

Revision ID: 9c0fff8aa6ab
Revises: 
Create Date: 2024-04-23 02:35:34.293901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9c0fff8aa6ab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry_record',
    sa.Column('record_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['students.studentid'], name='fk_entry_record_student_id'),
    sa.PrimaryKeyConstraint('record_id', name='pk_entry_record')
    )
    
    # entryrecords 테이블 삭제는 필요한 경우에만 진행해야 합니다.
    # op.drop_table('entryrecords')

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        # 필요없는 add_column, drop_column 명령 제거
        # 기존 컬럼명을 정확하게 사용하며, 필요없는 변경을 제거

    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seatnumber', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('studentid', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('phonenumber', sa.VARCHAR(length=15), autoincrement=False, nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.drop_column('seat_number')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('student_id')

    op.create_table('entryrecords',
    sa.Column('recordid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('studentid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('eventtype', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['studentid'], ['students.studentid'], name='entryrecords_studentid_fkey'),
    sa.PrimaryKeyConstraint('recordid', name='entryrecords_pkey')
    )
    op.drop_table('entry_record')
    # ### end Alembic commands ###