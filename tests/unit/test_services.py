from datetime import datetime
import pytest
from users.adapters import repository
from users.domain import model
from users.service_layer import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, users):
        self._users = users

    def add(self, user):
        self._users.append(user)

    def get(self, ssn):
        return next((u for u in self._users if u.ssn == ssn), None)

    def get_all(self, offset, limit, **kwargs):
        return self._paginate(self._filter(self._users, **kwargs), offset, limit)

    # helper methods
    def _filter(self, users, **kwargs):
        result = users
        if kwargs.get("first_name"):
            result = [u for u in users if u.first_name == kwargs["first_name"]]
        if kwargs.get("last_name"):
            result = [u for u in users if u.last_name == kwargs["last_name"]]
        if kwargs.get("date_of_birth"):
            result = [u for u in users if u.date_of_birth == kwargs["date_of_birth"]]
        return result

    def _paginate(self, users, offset, limit):
        result = users[offset:offset+limit+1]
        if next_page := len(result) > limit:
            result = result[:-1]
        return {"users": result, "next_page": next_page}


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.users = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_user():
    uow = FakeUnitOfWork()

    services.add_user("111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date(), uow)

    assert uow.users.get("111-1111-111") is not None
    assert uow.committed


def test_add_user_raise_error_if_underage():
    uow = FakeUnitOfWork()

    with pytest.raises(services.UserIsUnderage):
        services.add_user("111-1111-111", "John", "Doe", datetime.fromisoformat("2010-03-19").date(), uow)


def test_get_user():
    uow = FakeUnitOfWork()
    inserted_user = model.User("111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date())
    uow.users.add(inserted_user)

    fetched_user = services.get_user("111-1111-111", uow)

    assert fetched_user == inserted_user


def test_get_user_raise_error_if_doesnt_exist():
    uow = FakeUnitOfWork()

    with pytest.raises(services.UserDoesNotExist):
        services.get_user("111-1111-111", uow)


def test_get_users_pagination():
    uow = FakeUnitOfWork()
    uow.users.add(model.User("111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date()))
    uow.users.add(model.User("222-2222-222", "Jane", "Doe", datetime.fromisoformat("1986-11-07").date()))
    uow.users.add(model.User("333-3333-333", "Bob", "Bobby", datetime.fromisoformat("2001-08-13").date()))

    result = services.get_users(page_size = 2, current_page = 1, uow = uow)

    assert len(result["users"]) == 2
    assert result["next_page"]

    result = services.get_users(page_size = 2, current_page = 2, uow = uow)

    assert len(result["users"]) == 1
    assert result["next_page"] is False


def test_get_users_filter():
    uow = FakeUnitOfWork()
    uow.users.add(model.User("111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date()))
    uow.users.add(model.User("222-2222-222", "Jane", "Doe", datetime.fromisoformat("1986-11-07").date()))
    uow.users.add(model.User("333-3333-333", "Bob", "Bobby", datetime.fromisoformat("2001-08-13").date()))

    filter_by = {"last_name": "Doe"}
    result = services.get_users(page_size = 5, current_page = 1, uow = uow, **filter_by)

    assert len(result["users"]) == 2
    assert result["next_page"] is False
