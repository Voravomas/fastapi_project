from fastapi import FastAPI, Response, status
from mongoengine import connect
import json


from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField


class Employee(Document):
    id = IntField(required=True, primary_key=True)

    first_name = StringField()
    last_name = StringField()
    patronymic = StringField()
    corp_email = StringField(default="example@gmail.com")
    personal_email = StringField(default="example@gmail.com")
    phone_number = StringField(default="+380000000000")
    country = StringField(default="Ukraine")
    state = StringField()
    city = StringField()
    address = StringField()
    postcode = StringField()
    birthday = DateTimeField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    is_active = BooleanField(default=True)
    is_approved = BooleanField(default=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, first_name={self.first_name}, last_name={self.last_name})>"


app = FastAPI()

# Client
connect(host="mongodb://127.0.0.1:27017/employee")


# GET


@app.get("/")
async def root():
    return {"INDEX"}


@app.get("/api/v1/employees")
async def get_employees(response: Response):
    response.status_code = status.HTTP_200_OK
    res = [json.loads(x.to_json()) for x in Employee.objects()]
    return res


@app.get("/api/v1/employee/{emp_id}")
async def get_employee(emp_id: int, response: Response):
    res = Employee.objects(id=emp_id)
    if not res:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "NOT FOUND"
    else:
        return res


#### DELETE
@app.post("/api/v1/employee/{emp_id}")
async def create_employee(emp_id: int, response: Response):
    newEmp = Employee()
    newEmp.first_name = "X" * emp_id
    newEmp.last_name = "Y" * emp_id
    newEmp.id = emp_id
    newEmp.save()
    response.status_code = status.HTTP_200_OK
    return "OK"

# POST (CREATE empty)
#
#
# @app.post("/api/v1/employee/{emp_id}")
# async def create_employee(emp_id: int, response: Response):
#     with engine.connect() as conn:
#         s = select(Employee).where(Employee.id == emp_id)
#         res = conn.execute(s).all()
#     if not res:
#         em1 = Employee(id=emp_id, first_name=None)
#         Session = sessionmaker(bind=engine)
#         session = Session()
#         session.add(em1)
#         session.commit()
#         return "SUCCESS"
#     else:
#         response.status_code = status.HTTP_403_FORBIDDEN
#         return "ERROR: EXISTS"
#
#
# # DELETE (delete)
#
#
# @app.delete("/api/v1/employee/{emp_id}")
# async def delete_employee(emp_id: int, response: Response):
#     with engine.connect() as conn:
#         s = select(Employee).where(Employee.id == emp_id)
#         res = conn.execute(s).all()
#     if res:
#         Session = sessionmaker(bind=engine)
#         session = Session()
#         session.query(Employee).filter_by(id=emp_id).delete()
#         session.commit()
#         response.status_code = status.HTTP_200_OK
#         return "OK"
#     else:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return "ERROR: EMPLOYEE NOT FOUND"
#
#
# # PATCH (fill new)
#
#
# @app.patch("/api/v1/employee/{emp_id}")
# async def modify_employee(emp_id: int, first_name: str, last_name: str, response: Response,
#                           patronymic: str, corp_email: Optional[str] = "example@gmail.com",
#                           personal_email: Optional[str] = "example@gmail.com",
#                           phone_number: Optional[str] = "+3800000000000", country: Optional[str] = "Ukraine",
#                           state: Optional[str] = None, city: Optional[str] = None, address: Optional[str] = None,
#                           postcode: Optional[str] = None, birthday: Optional[datetime] = None,
#                           start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
#                           is_active: Optional[bool] = True, is_approved: Optional[bool] = True
#                           ):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     employee = session.query(Employee).filter_by(id=emp_id)[0]
#     if not employee:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return "ERROR: EMPLOYEE NOT FOUND"
#     if not employee.first_name and not employee.last_name:
#         employee.first_name = first_name
#         employee.last_name = last_name
#         employee.patronymic = patronymic
#         employee.corp_email = corp_email
#         employee.personal_email = personal_email
#         employee.phone_number = phone_number
#         employee.country = country
#         employee.state = state
#         employee.city = city
#         employee.address = address
#         employee.postcode = postcode
#         employee.birthday = birthday
#         employee.start_date = start_date
#         employee.end_date = end_date
#         employee.is_active = is_active
#         employee.is_approved = is_approved
#
#         session.add(employee)
#         session.commit()
#         response.status_code = status.HTTP_200_OK
#         return "OK"
#
#     else:
#         response.status_code = status.HTTP_403_FORBIDDEN
#         return "ERROR: EMPLOYEE NOT EMPTY"
#
#
# # PUT (replace)
#
#
# @app.put("/api/v1/employee/{emp_id}")
# async def replace_employee(emp_id: int, first_name: str, last_name: str, response: Response,
#                            patronymic: str, corp_email: Optional[str] = "example@gmail.com",
#                            personal_email: Optional[str] = "example@gmail.com",
#                            phone_number: Optional[str] = "+3800000000000", country: Optional[str] = "Ukraine",
#                            state: Optional[str] = None, city: Optional[str] = None, address: Optional[str] = None,
#                            postcode: Optional[str] = None, birthday: Optional[datetime] = None,
#                            start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
#                            is_active: Optional[bool] = True, is_approved: Optional[bool] = True
#                            ):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     employee = session.query(Employee).filter_by(id=emp_id)[0]
#     if not employee:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return "ERROR: EMPLOYEE NOT FOUND"
#     employee.first_name = first_name
#     employee.last_name = last_name
#     employee.patronymic = patronymic
#     employee.corp_email = corp_email
#     employee.personal_email = personal_email
#     employee.phone_number = phone_number
#     employee.country = country
#     employee.state = state
#     employee.city = city
#     employee.address = address
#     employee.postcode = postcode
#     employee.birthday = birthday
#     employee.start_date = start_date
#     employee.end_date = end_date
#     employee.is_active = is_active
#     employee.is_approved = is_approved
#
#     session.add(employee)
#     session.commit()
#     response.status_code = status.HTTP_200_OK
#     return "OK"
