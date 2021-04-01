from datetime import datetime


class Employee(object):
    """
    Class Employee that represents employee.
    :param s_id:  id of employee int
    :param first_name: first name of employee str
    :param last_name: last name of employee str
    :param patronymic: patronymic of employee str
    :param corp_email: corporate email of employee str
    :param personal_email: private email of employee str
    :param phone_number: phone number of employee str
    :param country: country of employee str
    :param state: state of employee str
    :param city: city of employee str
    :param address: address  of employee
    :param postcode: postcode of employee str
    :param birthday: birthday of employee str(DATETIME)
    :param start_date: start date of employee str(DATETIME)
    :param end_date: end date of employee str(DATETIME)
    :param is_active: is active employee str(bool)
    :param is_approved: is approved employee str(bool)e
    """
    def __init__(self, s_id: int, first_name: str, last_name: str, patronymic: str):
        """
        Initiate employee class
        :param s_id: unique id of Employee
        :param first_name: First name
        :param last_name: Last name
        :param patronymic: Patronymic
        """
        self.id = s_id
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.corp_email = "example@gmail.com"
        self.personal_email = "example@gmail.com"
        self.phone_number = "+380000000000"
        self.country = "Ukraine"
        self.state_ = ""
        self.city = ""
        self.address = ""
        self.postcode = ""
        self.birthday = str(datetime.now())
        self.start_date = str(datetime.now())
        self.end_date = str(datetime.now())
        self.is_active = str(True)
        self.is_approved = str(True)

    def __init_from_dict__(self, dictionary):
        """
        Method that allows to load Employee attributes directly from dictionary
        :param dictionary:
        :return: None
        """
        for k, v in dictionary.items():
            setattr(self, k, v)

    def __repr__(self):
        """
        How Employee represents
        :return:
        """
        return f"<Employee(id={self.id}, first_name={self.first_name}, last_name={self.last_name})>"
