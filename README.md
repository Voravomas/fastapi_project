# fastapi_project
## Description
fastaspi_project a.k.a. EmployeeProject contains information about employees via different databases (*PostgreSQL, MongoDB, DynamoDB*).

Currently the most developed version is built upon **PostgreSQL**. It includes:
- building database via migrations (SQLAlchemy, Alembic)
- handling HTTP methods (GET, POST, PUT, DELETE, PATCH), which communicate with db
- fast deployment via Docker

## Prerequisites
In order to use EmployeeProject you need:
- Docker
- Git
- curl

## Installation
`git clone https://github.com/Voravomas/fastapi_project.git` <br/>
`git checkout test_branch`

`sudo docker build -t ep_psql .`<br/>
`sudo docker-compose -f docker-compose.yml up`

## Usage
To check if db is up (should return "**{}**"):<br/>
`curl -GET http://0.0.0.0:8000/`

Get all employees:<br/>
`curl -GET http://0.0.0.0:8000/api/v1/employees`

Create empty employee:<br/>
`curl -POST http://0.0.0.0:8000/api/v1/employee/30`

Fill employee info:<br/>
`curl -PATCH http://0.0.0.0:8000/api/v1/employee/30?first_name=Alex&last_name=White&patronymic=Alex&country=US `

See new employee:<br/>
`curl -GET http://0.0.0.0:8000/api/v1/employee/30`
