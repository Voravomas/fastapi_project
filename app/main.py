from fastapi import FastAPI, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm


import schemas
from user_crud import create_user, read_users_me, \
    get_current_active_user, get_users, login_for_access_token, oauth2_scheme, replace_user
from employee_crud import get_employees, get_employee,\
    create_employee, delete_employee, modify_employee, replace_employee


app = FastAPI()


@app.get("/")
async def root():
    """
    Sample Get request
    """
    return {}


@app.post("/token")
async def login_for_access_token_here(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


@app.get("/users/me")
async def read_users_me_here(current_user: schemas.User = Depends(get_current_active_user)):
    return await read_users_me(current_user)


@app.get("/api/v1/users")
async def get_users_here(response: Response):
    return await get_users(response)


@app.post("/api/v1/user/{id}")
async def create_user_here(usr: schemas.User, response: Response):
    return await create_user(usr, response)


@app.put("/api/v1/user/{u_id}")
async def replace_user_here(usr: schemas.User, response: Response):
    return await replace_user(usr, response)


@app.get("/api/v1/employees")
async def get_employees_here(response: Response, token: str = Depends(oauth2_scheme)):
    return await get_employees(response, token)


@app.get("/api/v1/employee/{emp_id}")
async def get_employee_here(employee: schemas.EmployeeId, response: Response,
                            token: str = Depends(oauth2_scheme)):
    return await get_employee(employee, response, token)


@app.post("/api/v1/employee/{emp_id}")
async def create_employee_here(employee: schemas.EmployeeId, response: Response,
                               token: str = Depends(oauth2_scheme)):
    return await create_employee(employee, response, token)


@app.delete("/api/v1/employee/{emp_id}")
async def delete_employee_here(employee: schemas.EmployeeId, response: Response,
                               token: str = Depends(oauth2_scheme)):
    return await delete_employee(employee, response, token)


@app.patch("/api/v1/employee/{emp_id}")
async def modify_employee_here(employee: schemas.Employee, response: Response,
                               token: str = Depends(oauth2_scheme)):
    return await modify_employee(employee, response, token)


# PUT (replace)
@app.put("/api/v1/employee/{emp_id}")
async def replace_employee_here(employee: schemas.Employee, response: Response,
                                token: str = Depends(oauth2_scheme)):
    return await replace_employee(employee, response, token)
