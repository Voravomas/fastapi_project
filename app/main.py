from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os import getenv
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext


from database import Employee, User

app = FastAPI()


def get_path():
    return "postgresql://{}:{}@{}/{}".format(getenv('PSQL_LOG'),
                                             getenv('PSQL_PASS'),
                                             getenv('PSQL_URL'),
                                             getenv('PSQL_DB_NAME'))


# Engine
db_path = get_path()
engine = create_engine(db_path, echo=True, future=True)


# user_db = dict()
# log_dict = dict()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "3703ddb8e48220ba2ca5cf03f17f61685ea0fca3b0d934899048ca80eb21f129"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# class User(BaseModel):
#     username: str
#     email: Optional[str] = None
#     full_name: Optional[str] = None
#     disabled: Optional[bool] = None


# class UserInDB(User):
#     hashed_password: str


@app.get("/")
async def root():
    """
    Sample Get request
    """
    return {}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_users_obj():
    all_users = list()
    vals = await get_users(Response())
    for usr_vals in vals:
        temp_usr = User()
        temp_usr.__init_from_vals__(usr_vals)
        all_users.append(temp_usr)
    return all_users


def get_user_obj(db, username: str):
    for usr in db:
        if usr.username == username:
            return usr
    return None


def authenticate_user(db, username: str, password: str):
    user = get_user_obj(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    db = await get_users_obj()
    print("DB IS: ", db)
    user = get_user_obj(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Invalid user")
    return current_user


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/api/v1/users")
async def get_users(response: Response):
    with engine.connect() as conn:
        s = select(User)
        res = conn.execute(s)
    response.status_code = status.HTTP_200_OK
    return res.all()


@app.post("/api/v1/user/{u_id}")
async def create_user(u_id: int, username: str, password: str, response: Response):
    with engine.connect() as conn:
        s = select(User).where(User.id == u_id)
        res = conn.execute(s).all()
    if not res:
        em1 = User(id=u_id, username=username, hashed_password=get_password_hash(password))
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(em1)
        session.commit()
        return "SUCCESS"
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return "ERROR: EXISTS"


@app.put("/api/v1/user/{u_id}")
async def replace_user(u_id: int, response: Response, username: Optional[str] = None, full_name: Optional[str] = None,
                       password: Optional[str] = None, email: Optional[str] = None, privilege: Optional[str] = None,
                       disabled: Optional[str] = None):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(id=u_id)[0]
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "ERROR: USER NOT FOUND"
    print(full_name)
    user.username = username if username else user.username
    user.full_name = full_name if full_name else user.full_name
    user.hashed_password = get_password_hash(password) if password else user.hashed_password
    user.email = email if email else user.email
    user.disabled = disabled if disabled else user.disabled
    user.privilege = privilege if privilege else user.privilege
    session.add(user)
    session.commit()
    response.status_code = status.HTTP_200_OK
    return "OK"


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
