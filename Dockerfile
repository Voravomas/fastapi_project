FROM python:3.8-buster
MAINTAINER Mykyta Samovarov <nikita.samovarov@gmail.com>

# Copy EmployeeProject
COPY . .

# Install needed python packages
RUN pip3 install -r requirements.txt

# Set working directory
WORKDIR app/

# Set exectutable rules to entrypoint file
RUN chmod 777 startup.sh

# Entrypoint
ENTRYPOINT ["./startup.sh"]

