from datetime import datetime
import pytest
from sqlalchemy.sql import text
from users.domain import model
from users.service_layer import unit_of_work


def insert_user(session, ssn, first_name, last_name, date_of_birth):
    session.execute(
        text("INSERT INTO users (ssn, first_name, last_name, date_of_birth)"
            " VALUES (:ssn, :first_name, :last_name, :date_of_birth)"),
        dict(ssn=ssn, first_name=first_name, last_name=last_name, date_of_birth=date_of_birth),
    )


def get_user(session, ssn):
    [user] = session.execute(
        text("SELECT ssn FROM users WHERE ssn=:ssn"),
        dict(ssn=ssn),
    )
    return user


def test_uow_can_add_user(session_factory):
    session = session_factory()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        uow.users.add(model.User("111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date()))
        uow.commit()

    user = get_user(session, "111-1111-111")
    assert user.ssn == "111-1111-111"


def test_uow_can_fetch_user(session_factory):
    session = session_factory()
    insert_user(session, "111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date())
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user = uow.users.get("111-1111-111")
        uow.commit()

    assert user.ssn == "111-1111-111"


def test_uow_can_fetch_users(session_factory):
    session = session_factory()
    insert_user(session, "111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date())
    insert_user(session, "222-2222-222", "Jane", "Doe", datetime.fromisoformat("1986-11-07").date())
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        result = uow.users.get_all(0, 20)
        uow.commit()

    assert len(result["users"]) == 2
    assert result["next_page"] is False


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_user(uow.session, "111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date())

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "users"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_user(uow.session, "111-1111-111", "John", "Doe", datetime.fromisoformat("1997-03-19").date())
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "users"')))
    assert rows == []
