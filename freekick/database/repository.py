from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    session: Any = None

    @abstractmethod
    def get(self, entity):
        pass

    @abstractmethod
    def add(self, instance):
        pass

    @abstractmethod
    def commit(self):
        pass


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity):
        return self.session.get(entity=entity)

    def add(self, instance):
        self.session.add(instance=isinstance)

    def commit(self):
        self.session.commit()


class MockRepository(AbstractRepository):
    # TODO: In-Memory repository used for integration testing.
    def __init__(self) -> None:
        pass

    def get(self, entity):
        pass

    def add(self, instance):
        pass

    def commit(self):
        pass
