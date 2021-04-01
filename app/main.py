from botocore.exceptions import ClientError
from fastapi import FastAPI, Response, status
from boto3 import resource
from datetime import datetime

from keys import ACCESS_ID, ACCESS_KEY
from employee import Employee

app = FastAPI()

# Engine
dynamo_db = resource('dynamodb', endpoint_url="http://dynamodb.eu-central-1.amazonaws.com/",
                     region_name='eu-central-1',
                     aws_access_key_id=ACCESS_ID,
                     aws_secret_access_key=ACCESS_KEY)
table = dynamo_db.Table('Employee')


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
    :return: Dict of Employee instances
    """
    try:
        result = table.scan()
    except ClientError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        print(e.response['Error']['Message'])
    else:
        response.status_code = status.HTTP_200_OK
        return result['Items']


@app.get("/api/v1/employee/{emp_id}")
async def get_employee(emp_id: int, response: Response):
    """
    Function that returns exact employee if found, else "ERROR: NOT FOUND" str
    :param emp_id: id of employee int
    :param response:
    :return: Dict Employee instance or "ERROR: NOT FOUND" str
    """
    try:
        resp_from_server = table.get_item(Key={'id': emp_id})
    except ClientError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        print(e.response['Error']['Message'])
        return e.response['Error']['Message']
    if not resp_from_server or "Item" not in resp_from_server:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: NOT FOUND"
    else:
        response.status_code = status.HTTP_200_OK
        return resp_from_server["Item"]


@app.post("/api/v1/employee/{emp_id}")
async def create_employee(emp_id: int, response: Response):
    """
    Function that creates general record in DB with default params with empty name, surname, patronymic
    :param emp_id: id of employee int
    :param response:
    :return: "SUCCESS" str if success, or "ERROR: EXISTS" str if error
    """
    if_found = await get_employee(emp_id, response=response)
    if if_found == "ERROR: NOT FOUND":
        emp = Employee(emp_id, "", "", "")
        resp_from_server = table.put_item(Item=emp.__dict__)
        response.status_code = status.HTTP_200_OK
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
    if_found = await get_employee(emp_id, response=response)
    if if_found != "ERROR: NOT FOUND":
        try:
            resp_from_server = table.delete_item(Key={'id': emp_id})
            print(resp_from_server)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
                raise
            else:
                raise
        else:
            response.status_code = status.HTTP_200_OK
            return "OK"
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"


async def upd_expr(emp_class):
    """
    Function that transforms employee attributes into required form
    for UpdateExpression attribute during update
    :param emp_class: Employee
    :return: str
    """
    res = emp_class.__dict__.keys()
    res_str = "set "
    for i in res:
        if i == "id":
            continue
        res_str += "{}=:{}, ".format(i, i)
    return res_str[:-2]


async def exp_attr_v(emp_class):
    """
    Function that creates new dict out of Employee attributes in required form
    for ExpressionAttributeValues attribute during update
    :param emp_class: Employee
    :return: dict
    """
    old_d = emp_class.__dict__
    new_d = dict()
    for el in old_d.keys():
        if el == "id":
            continue
        new_d[":" + el] = old_d[el]
    return new_d


async def fill_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                        patronymic: str, corp_email="example@gmail.com",
                        personal_email="example@gmail.com",
                        phone_number="+3800000000000", country="Ukraine",
                        state_="", city="", address="",
                        postcode="", birthday=str(datetime.now()),
                        start_date=str(datetime.now()), end_date=str(datetime.now()),
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
    :param state_: state_ of employee str
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
    if_found = await get_employee(emp_id, response=response)
    employee = Employee(emp_id, "", "", "")
    employee.__init_from_dict__(if_found)
    # modifying data in class
    employee.first_name = first_name
    employee.last_name = last_name
    employee.patronymic = patronymic
    employee.corp_email = corp_email
    employee.personal_email = personal_email
    employee.phone_number = phone_number
    employee.country = country
    employee.state_ = state_
    employee.city = city
    employee.address = address
    employee.postcode = postcode
    employee.birthday = birthday
    employee.start_date = start_date
    employee.end_date = end_date
    employee.is_active = is_active
    employee.is_approved = is_approved
    # commit data
    expr_to_send = await upd_expr(employee)
    val_to_send = await exp_attr_v(employee)
    response_from_server = table.update_item(
        Key={
            'id': emp_id,
        },
        UpdateExpression=expr_to_send,
        ExpressionAttributeValues=val_to_send,
        ReturnValues="UPDATED_NEW"
    )
    response.status_code = status.HTTP_200_OK
    return "OK"


@app.patch("/api/v1/employee/{emp_id}")
async def modify_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                          patronymic: str, corp_email="example@gmail.com",
                          personal_email="example@gmail.com",
                          phone_number="+3800000000000", country="Ukraine",
                          state_="", city="", address="",
                          postcode="", birthday=str(datetime.now()),
                          start_date=str(datetime.now()), end_date=str(datetime.now()),
                          is_active=True, is_approved=True
                          ):
    """
    Function modifies only newly created Employees.
    It will not work if user already has name or surname or patronymic
    :param emp_id:  id of employee int
    :param first_name: first name of employee str
    :param last_name: last name of employee str
    :param response:
    :param patronymic: patronymic of employee str
    :param corp_email: corporate email of employee str
    :param personal_email: private email of employee str
    :param phone_number: phone number of employee str
    :param country: country of employee str
    :param state_: state_ of employee str
    :param city: city of employee str
    :param address: address  of employee
    :param postcode: postcode of employee str
    :param birthday: birthday of employee DATETIME
    :param start_date: start date of employee DATETIME
    :param end_date: end date of employee DATETIME
    :param is_active: is active employee bool
    :param is_approved: is approved employee bool
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user
    :return: "OK" if success, "ERROR: EMPLOYEE NOT FOUND" if there is no such user,
    "ERROR: EMPLOYEE NOT EMPTY" if user object does not have default attributes
    """
    if_found = await get_employee(emp_id, response=response)
    if if_found == "ERROR: NOT FOUND":
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    if (if_found["first_name"] == "") and (if_found["last_name"] == "") and (if_found["patronymic"] == ""):
        return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                                   patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                                   phone_number=phone_number, country=country, state_=state_, city=city,
                                   address=address, postcode=postcode, birthday=birthday,
                                   start_date=start_date, end_date=end_date,
                                   is_active=is_active, is_approved=is_approved)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EMPLOYEE NOT EMPTY"


@app.put("/api/v1/employee/{emp_id}")
async def replace_employee(emp_id: int, first_name: str, last_name: str, response: Response,
                           patronymic: str, corp_email="example@gmail.com",
                           personal_email="example@gmail.com",
                           phone_number="+3800000000000", country="Ukraine",
                           state_="", city="", address="",
                           postcode="", birthday=str(datetime.now()),
                           start_date=str(datetime.now()), end_date=str(datetime.now()),
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
    :param state_: state_ of employee str
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
    if_found = await get_employee(emp_id, response=response)
    if if_found == "ERROR: NOT FOUND":
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: EMPLOYEE NOT FOUND"
    return await fill_employee(emp_id=emp_id, first_name=first_name, last_name=last_name, response=response,
                               patronymic=patronymic, corp_email=corp_email, personal_email=personal_email,
                               phone_number=phone_number, country=country, state_=state_, city=city, address=address,
                               postcode=postcode, birthday=birthday, start_date=start_date, end_date=end_date,
                               is_active=is_active, is_approved=is_approved)
