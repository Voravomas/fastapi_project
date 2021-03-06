"""Adding data

Revision ID: 952bbcd2f9e0
Revises: fca06a7239cd
Create Date: 2021-03-26 13:40:35.495256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '952bbcd2f9e0'
down_revision = 'fca06a7239cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    data = [
        {"first_name": "Myk", "last_name": "Sam", "patronymic": "Oleks", "corp_email": "aa@gm.com",
         "personal_email": "aa@gm.com", "phone_number": "123", "country": "Ukraine", "state": "KI",
         "city": "Kyiv", "address": "asd", "postcode": "04123", "birthday": "1999-01-01",
         "start_date": "1999-01-01", "end_date": "1999-01-01", "is_active": True, "is_approved": True}
    ]
    my_table = sa.Table("employees", sa.MetaData(bind=op.get_bind()), autoload=True)
    op.bulk_insert(my_table, data)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM employees WHERE id = 1;")
    # ### end Alembic commands ###
