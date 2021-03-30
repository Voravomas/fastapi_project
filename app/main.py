from fastapi import FastAPI, Response, status
import pymongo
from db_mongo import Employee
from datetime import datetime

# create app
app = FastAPI()

# create connection to db
url = "mongodb://127.0.0.1:27017/"
client = pymongo.MongoClient(url)
db = client["employee"]


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
    :param response:
    :return: list of dicts (Employee instances)
    """
    response.status_code = status.HTTP_200_OK
    res = [x for x in db.employee.find()]
    return res


@app.get("/api/v1/employee/{emp_id}")
async def get_employee(emp_id: int, response: Response):
    """
    Function that returns exact employee if found, else "ERROR: NOT FOUND" str
    :param emp_id: id of employee int
    :param response:
    :return: dict (single Employee instance)
    """
    # get all employees
    coll = db.employee.find()
    # find needed (res) employee with id=emp_id
    res = None
    for el in coll:
        if el["_id"] == emp_id:
            res = el
            break
    if not res:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: NOT FOUND"
    else:
        return res


@app.post("/api/v1/employee/{emp_id}")
async def create_employee(emp_id: int, response: Response):
    """
    Function that creates general record in DB with default params with empty name
    :param emp_id: id of employee int
    :param response:
    :return: ID of newly created employee, or "ERROR: EXISTS" str if error
    """
    if_exist = await get_employee(emp_id, response)
    if isinstance(if_exist, dict):
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"
    else:
        newEmp = Employee(s_id=emp_id, first_name="", last_name="", patronymic="")
        # here newEmp.__dict__ transforms class object into json-like format
        emp_id = db.employee.insert_one(newEmp.__dict__).inserted_id
        response.status_code = status.HTTP_201_CREATED
        return str(emp_id)


@app.delete("/api/v1/employee/{emp_id}")
async def delete_employee(emp_id: int, response: Response):
    """
    Function deletes employee if it was found
    :param emp_id: id of employee int
    :param response:
    :return: "OK" str if success, "ERROR: EMPLOYEE NOT FOUND" else
    """
    if_exist = await get_employee(emp_id, response)
    if isinstance(if_exist, dict):
        query = {"_id": emp_id}
        db.employee.delete_one(query)
        response.status_code = status.HTTP_200_OK
        return "OK"
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"


async def fill_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                        patronymic: str, corp_email="example@gmail.com",
                        personal_email="example@gmail.com",
                        phone_number="+3800000000000", country="Ukraine",
                        state="", city="", address="",
                        postcode="", birthday=datetime.now(),
                        start_date=datetime.now(), end_date=datetime.now(),
                        is_active=True, is_approved=True
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
    cur_emp = await get_employee(emp_id, response)
    cur_emp["first_name"] = first_name
    cur_emp["last_name"] = last_name
    cur_emp["patronymic"] = patronymic
    cur_emp["corp_email"] = corp_email
    cur_emp["personal_email"] = personal_email
    cur_emp["phone_number"] = phone_number
    cur_emp["country"] = country
    cur_emp["state"] = state
    cur_emp["city"] = city
    cur_emp["address"] = address
    cur_emp["postcode"] = postcode
    cur_emp["birthday"] = birthday
    cur_emp["start_date"] = start_date
    cur_emp["end_date"] = end_date
    cur_emp["is_active"] = is_active
    cur_emp["is_approved"] = is_approved
    db.employee.update_one({"_id": emp_id}, {"$set": cur_emp})
    response.status_code = status.HTTP_200_OK
    return "OK"


@app.patch("/api/v1/employee/{emp_id}")
async def modify_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                          patronymic: str, corp_email="example@gmail.com",
                          personal_email="example@gmail.com",
                          phone_number="+3800000000000", country="Ukraine",
                          state="", city="", address="",
                          postcode="", birthday=datetime.now(),
                          start_date=datetime.now(), end_date=datetime.now(),
                          is_active=True, is_approved=True
                          ):
    """
    Function modifies only newly created Employees. It will not work if user already has name
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
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user,
    "ERROR: EMPLOYEE NOT EMPTY" if user object does not have default attributes
    """
    if_exist = await get_employee(emp_id, response)
    if not isinstance(if_exist, dict):
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    cur_emp = if_exist
    if not cur_emp["first_name"] and not cur_emp["last_name"]:
        return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                                   patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                                   phone_number=phone_number, country=country, state=state, city=city, address=address,
                                   postcode=postcode, birthday=birthday, start_date=start_date, end_date=end_date,
                                   is_active=is_active, is_approved=is_approved)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EMPLOYEE NOT EMPTY"


@app.put("/api/v1/employee/{emp_id}")
async def replace_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                           patronymic: str, corp_email="example@gmail.com",
                           personal_email="example@gmail.com",
                           phone_number="+3800000000000", country="Ukraine",
                           state="", city="", address="",
                           postcode="", birthday=datetime.now(),
                           start_date=datetime.now(), end_date=datetime.now(),
                           is_active=True, is_approved=True
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
    if_exist = await get_employee(emp_id, response)
    if not isinstance(if_exist, dict):
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                               patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                               phone_number=phone_number, country=country, state=state, city=city, address=address,
                               postcode=postcode, birthday=birthday, start_date=start_date, end_date=end_date,
                               is_active=is_active, is_approved=is_approved)
