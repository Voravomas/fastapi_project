from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    hashed_password: str
    disabled: Optional[bool] = False
    privilege: Optional[int] = 1   # 0-nothing, 1-read, 2-read/write,

    class Config:
        orm_mode = True


class EmployeeId(BaseModel):
    id: int


class EmployeeCreate(EmployeeId):
    first_name: str
    last_name: str
    patronymic: str


class Employee(EmployeeCreate):
    """
    :param id:  id of employee int
    :param first_name: first name of employee str
    :param last_name: last name of employee str
    :param response:
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
    corp_email: Optional[str] = "example@gmail.com"
    personal_email: Optional[str] = "example@gmail.com"
    phone_number: Optional[str] = "+380000000000"
    country: Optional[str] = "Ukraine"
    state: Optional[str] = str(None)
    city: Optional[str] = str(None)
    address: Optional[str] = str(None)
    postcode: Optional[str] = str(None)
    birthday: Optional[str] = str(datetime.utcnow())
    start_date: Optional[str] = str(datetime.utcnow())
    end_date: Optional[str] = str(datetime.utcnow())
    is_active: Optional[bool] = True
    is_approved: Optional[bool] = True

    class Config:
        orm_mode = True
