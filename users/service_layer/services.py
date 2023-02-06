from datetime import date

from users.domain.model import User
from users.service_layer import unit_of_work


class UserIsUnderage(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


def is_of_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age >= 18


def add_user(
    ssn: str, first_name: str, last_name: str, date_of_birth: date,
    uow: unit_of_work.AbstractUnitOfWork,
):
    if not is_of_age(date_of_birth):
        raise UserIsUnderage()
    with uow:
        user = User(ssn=ssn, first_name=first_name, last_name=last_name, date_of_birth = date_of_birth)
        uow.users.add(user)
        uow.commit()


def get_user(ssn: str, uow: unit_of_work.AbstractUnitOfWork,) -> dict:
    with uow:
        user = uow.users.get(ssn=ssn)
        uow.commit()
    if not user:
        raise UserDoesNotExist()
    return user


def get_users(current_page: int, page_size: int, uow: unit_of_work.AbstractUnitOfWork, **kwargs) -> dict:
    with uow:
        result = uow.users.get_all(offset=(current_page-1)*page_size, limit=page_size, **kwargs)
        uow.commit()
    result["current_page"] = current_page
    result["page_size"] = page_size
    return result
