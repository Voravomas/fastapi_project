from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, String, Date, create_engine, select
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    corp_email = Column(String, default="example@gmail.com")
    personal_email = Column(String, default="example@gmail.com")
    phone_number = Column(String, default="+380000000000")
    country = Column(String, default="Ukraine")
    state = Column(String)
    city = Column(String)
    address = Column(String)
    postcode = Column(String)
    birthday = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, first_name={self.first_name}, last_name={self.last_name})>"


engine = create_engine("postgresql://postgres:postgres@localhost:5432/work", echo=True, future=True)

emp_id = 3
Session = sessionmaker(bind=engine)
session = Session()
# stmt = select(Employee).filter_by(id=emp_id)
# res = session.execute(stmt)
# for el in res:
#     print()
# session.query(select(Employee).filter_by(id=emp_id))
# session.execute()
result = session.query(Employee).filter_by(id=emp_id)

# print(type(result[0]))
