from fastapi import Response, Depends, status
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker

import schemas
import models
from user_crud import oauth2_scheme, get_auth
from exceptions import invalid_role_exception
from database import engine


async def get_employees(response: Response, token: str = Depends(oauth2_scheme)):
    """
    Function that returns all employees in a db
    :return: List of <sqlalchemy.engine.row.Row'> Employee instances
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 1
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    with engine.connect() as conn:
        s = select(models.Employee)
        res = conn.execute(s)
    response.status_code = status.HTTP_200_OK
    return res.all()


async def get_employee(employee: schemas.EmployeeId, response: Response,
                       token: str = Depends(oauth2_scheme)):
    """
    Function that returns exact employee if found, else "ERROR: NOT FOUND" str
    :param emp_id: id of employee int
    :param response:
    :return: <class 'sqlalchemy.engine.row.Row'> Employee instance, "ERROR: NOT FOUND" str else
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 1
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    with engine.connect() as conn:
        s = select(models.Employee).where(models.Employee.id == employee.id)
        res = conn.execute(s).all()
    if not res:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: NOT FOUND"
    else:
        response.status_code = status.HTTP_200_OK
        return res


async def create_employee(employee: schemas.EmployeeId, response: Response,
                          token: str = Depends(oauth2_scheme)):
    """
    Function that creates general record in DB with default params with null name
    :param emp_id: id of employee int
    :param response:
    :return: "SUCCESS" str if success, or "ERROR: EXISTS" str if error
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 2
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    with engine.connect() as conn:
        s = select(models.Employee).where(models.Employee.id == employee.id)
        res = conn.execute(s).all()
    if not res:
        em1 = models.Employee(id=employee.id, first_name=None)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(em1)
        session.commit()
        return "SUCCESS"
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"


async def delete_employee(employee: schemas.EmployeeId, response: Response,
                          token: str = Depends(oauth2_scheme)):
    """
    Function deletes employee if it was found
    :param emp_id: id of employee int
    :param response:
    :return: "OK" str if success, "ERROR: EMPLOYEE NOT FOUND" else
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 2
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    with engine.connect() as conn:
        s = select(models.Employee).where(models.Employee.id == employee.id)
        res = conn.execute(s).all()
    if res:
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(models.Employee).filter_by(id=employee.id).delete()
        session.commit()
        response.status_code = status.HTTP_200_OK
        return "OK"
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"


async def fill_employee(employee: schemas.Employee, response: Response):
    """
    Function that fills employee with data provided
    :return: "OK". No checks are required,
    because they are done before calling this function
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    cur_employee = session.query(models.Employee).filter_by(id=employee.id)[0]
    # modifying data
    cur_employee.first_name = employee.first_name
    cur_employee.last_name = employee.last_name
    cur_employee.patronymic = employee.patronymic
    cur_employee.corp_email = employee.corp_email
    cur_employee.personal_email = employee.personal_email
    cur_employee.phone_number = employee.phone_number
    cur_employee.country = employee.country
    cur_employee.state = employee.state
    cur_employee.city = employee.city
    cur_employee.address = employee.address
    cur_employee.postcode = employee.postcode
    cur_employee.birthday = employee.birthday
    cur_employee.start_date = employee.start_date
    cur_employee.end_date = employee.end_date
    cur_employee.is_active = employee.is_active
    cur_employee.is_approved = employee.is_approved
    # commit data
    session.add(cur_employee)
    session.commit()
    response.status_code = status.HTTP_200_OK
    return "OK"


async def modify_employee(employee: schemas.Employee, response: Response,
                          token: str = Depends(oauth2_scheme)):
    """
    Function modifies only newly created Employees.
    It will not work if user already has name
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND"
    if there is no such user,
    "ERROR: EMPLOYEE NOT EMPTY"
    if user object does not have default attributes
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 2
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    Session = sessionmaker(bind=engine)
    session = Session()
    cur_employee = session.query(models.Employee).filter_by(id=employee.id)[0]
    if not cur_employee:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    if not cur_employee.first_name and not cur_employee.last_name:
        return await fill_employee(employee, response)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EMPLOYEE NOT EMPTY"


async def replace_employee(employee: schemas.Employee, response: Response,
                           token: str = Depends(oauth2_scheme)):
    """
    Function that modifies any user
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user
    """
    payload = await get_auth(token)
    ACCESS_ROLE = 2
    print(payload)
    if payload.get("role") < ACCESS_ROLE:
        raise invalid_role_exception

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        cur_employee = session.query(models.Employee).filter_by(id=employee.id)[0]
    except IndexError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    if not cur_employee:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    return await fill_employee(employee, response)
