import abc
from users.domain import model


class AbstractRepository(abc.ABC):
    '''
    abc = abstract base class

    Python will not let you instantiate a class that doesn't implement all the
    abstractmethod defined in its parent class.
    '''
    @abc.abstractmethod
    def add(self, user: model.User):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, ssn) -> model.User:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user):
        self.session.add(user)

    def get(self, ssn):
        return self.session.query(model.User).filter_by(ssn=ssn).first()

    def get_all(self, offset, limit, **kwargs):
        result = self.session.query(model.User).filter_by(**kwargs).offset(offset).limit(limit+1).all()
        if next_page := len(result) > limit:
            result = result[:-1]
        return {'users': result, 'next_page': next_page}
