from fastapi import FastAPI, Response, status
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Optional
from datetime import datetime

from database import Employee
from os import getenv


app = FastAPI()

def get_path():
	return "postgresql://{}:{}@{}/{}".format(os.getenv('PSQL_LOG'),\
						os.getenv('PSQL_PASS'),\
						os.getenv('PSQL_URL'),\
						os.getenv('PSQL_DB_NAME'))

# Engine
db_path = get_path()
engine = create_engine(db_path, echo=True, future=True)


@app.get("/")
async def root():
    """
    Sample Get request
    """
    return {}


@app.get("/api/v1/employees")
async def get_employees(response: Response):
    """
    Function that returns all employees in a db
    :return: List of <sqlalchemy.engine.row.Row'> Employee instances
    """
    with engine.connect() as conn:
        s = select(Employee)
        res = conn.execute(s)
    response.status_code = status.HTTP_200_OK
    return res.all()


@app.get("/api/v1/employee/{emp_id}")
async def get_employee(emp_id: int, response: Response):
    """
    Function that returns exact employee if found, else "ERROR: NOT FOUND" str
    :param emp_id: id of employee int
    :param response:
    :return: <class 'sqlalchemy.engine.row.Row'> Employee instance, "ERROR: NOT FOUND" str else
    """
    with engine.connect() as conn:
        s = select(Employee).where(Employee.id == emp_id)
        res = conn.execute(s).one()
    if not res:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: NOT FOUND"
    else:
        response.status_code = status.HTTP_200_OK
        return res


@app.post("/api/v1/employee/{emp_id}")
async def create_employee(emp_id: int, response: Response):
    """
    Function that creates general record in DB with default params with null name
    :param emp_id: id of employee int
    :param response:
    :return: "SUCCESS" str if success, or "ERROR: EXISTS" str if error
    """
    with engine.connect() as conn:
        s = select(Employee).where(Employee.id == emp_id)
        res = conn.execute(s).all()
    if not res:
        em1 = Employee(id=emp_id, first_name=None)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(em1)
        session.commit()
        return "SUCCESS"
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"


@app.delete("/api/v1/employee/{emp_id}")
async def delete_employee(emp_id: int, response: Response):
    """
    Function deletes employee if it was found
    :param emp_id: id of employee int
    :param response:
    :return: "OK" str if success, "ERROR: EMPLOYEE NOT FOUND" else
    """
    with engine.connect() as conn:
        s = select(Employee).where(Employee.id == emp_id)
        res = conn.execute(s).all()
    if res:
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(Employee).filter_by(id=emp_id).delete()
        session.commit()
        response.status_code = status.HTTP_200_OK
        return "OK"
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"


async def fill_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                        patronymic: str, corp_email: Optional[str] = "example@gmail.com",
                        personal_email: Optional[str] = "example@gmail.com",
                        phone_number: Optional[str] = "+3800000000000", country: Optional[str] = "Ukraine",
                        state: Optional[str] = None, city: Optional[str] = None, address: Optional[str] = None,
                        postcode: Optional[str] = None, birthday: Optional[datetime] = None,
                        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                        is_active: Optional[bool] = True, is_approved: Optional[bool] = True
                        ):
    """
    Function that fills employee with data provided
    :param emp_id:  id of employee int
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
    :return: "OK". No checks are required,
    because they are done before calling this function
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employee).filter_by(id=emp_id)[0]
    # modifying data
    employee.first_name = first_name
    employee.last_name = last_name
    employee.patronymic = patronymic
    employee.corp_email = corp_email
    employee.personal_email = personal_email
    employee.phone_number = phone_number
    employee.country = country
    employee.state = state
    employee.city = city
    employee.address = address
    employee.postcode = postcode
    employee.birthday = birthday
    employee.start_date = start_date
    employee.end_date = end_date
    employee.is_active = is_active
    employee.is_approved = is_approved
    # commit data
    session.add(employee)
    session.commit()
    response.status_code = status.HTTP_200_OK
    return "OK"


@app.patch("/api/v1/employee/{emp_id}")
async def modify_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                          patronymic: str, corp_email: Optional[str] = "example@gmail.com",
                          personal_email: Optional[str] = "example@gmail.com",
                          phone_number: Optional[str] = "+3800000000000", country: Optional[str] = "Ukraine",
                          state: Optional[str] = None, city: Optional[str] = None, address: Optional[str] = None,
                          postcode: Optional[str] = None, birthday: Optional[datetime] = None,
                          start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                          is_active: Optional[bool] = True, is_approved: Optional[bool] = True
                          ):
    """
    Function modifies only newly created Employees. It will not work if user already has name
    :param emp_id:
    :param first_name:
    :param last_name:
    :param response:
    :param patronymic:
    :param corp_email:
    :param personal_email:
    :param phone_number:
    :param country:
    :param state:
    :param city:
    :param address:
    :param postcode:
    :param birthday:
    :param start_date:
    :param end_date:
    :param is_active:
    :param is_approved:
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user,
    "ERROR: EMPLOYEE NOT EMPTY" if user object does not have default attributes
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employee).filter_by(id=emp_id)[0]
    if not employee:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    if not employee.first_name and not employee.last_name:
        return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                                   patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                                   phone_number=phone_number, country=country, state=state, city=city, address=address,
                                   postcode=postcode, birthday=birthday, start_date=start_date, end_date=end_date,
                                   is_active=is_active, is_approved=is_approved)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EMPLOYEE NOT EMPTY"


# PUT (replace)


@app.put("/api/v1/employee/{emp_id}")
async def replace_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                           patronymic: str, corp_email: Optional[str] = "example@gmail.com",
                           personal_email: Optional[str] = "example@gmail.com",
                           phone_number: Optional[str] = "+3800000000000", country: Optional[str] = "Ukraine",
                           state: Optional[str] = None, city: Optional[str] = None, address: Optional[str] = None,
                           postcode: Optional[str] = None, birthday: Optional[datetime] = None,
                           start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                           is_active: Optional[bool] = True, is_approved: Optional[bool] = True
                           ):
    """
        Function that modifies any user
    :param emp_id:  id of employee int
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
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    employee = session.query(Employee).filter_by(id=emp_id)[0]
    if not employee:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                               patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                               phone_number=phone_number, country=country, state=state, city=city, address=address,
                               postcode=postcode, birthday=birthday, start_date=start_date, end_date=end_date,
                               is_active=is_active, is_approved=is_approved)
