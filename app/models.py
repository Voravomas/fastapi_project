from sqlalchemy import Boolean, Column, Integer, String, Date
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, nullable=False)
    full_name = Column(String, default=None)
    email = Column(String, default=None)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    privilege = Column(Integer, default=1)   # 0-nothing, 1-read, 2-read/write,

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, privilege={self.privilege})>"

    def __init_from_vals__(self, vals):
        self.id, self.username, self.full_name, self.email, self.hashed_password, self.disabled, self.privilege = vals


class Employee(Base):
    """
    Class Employee from sqlalchemy declarative_base
    :param emp_id:  id of employee int
    :param first_name: first name of employee str
    :param last_name: last name of employee str
    :param patronymic: patronymic of employee str
    :param corp_email: corporate email of employee str
    :param personal_email: private email of employee str
    :param phone_number: phone number of employee str
    :param country: country of employee str
    :param state: state of employee str
    :param city: city of employee str
    :param address: address  of employee
    :param postcode: postcode of employee str
    :param birthday: birthday of employee DATETIME
    :param start_date: start date of employee DATETIME
    :param end_date: end date of employee DATETIME
    :param is_active: is active employee bool
    :param is_approved: is approved employee bool
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    corp_email = Column(String, default="example@gmail.com")
    personal_email = Column(String, default="example@gmail.com")
    phone_number = Column(String, default="+380000000000")
    country = Column(String, default="Ukraine")
    state = Column(String, default=str(None))
    city = Column(String, default=str(None))
    address = Column(String, default=str(None))
    postcode = Column(String, default=str(None))
    birthday = Column(Date, default=str(datetime.utcnow()))
    start_date = Column(Date, default=str(datetime.utcnow()))
    end_date = Column(Date, default=str(datetime.utcnow()))
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, first_name={self.first_name}, last_name={self.last_name})>"
