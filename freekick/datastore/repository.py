from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    session: Any = None

    @abstractmethod
    def get(self, entity: Any, reference: Any) -> Any:
        pass

    @abstractmethod
    def add(self, instance: Any) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass


class SQLAlchemyRepository(AbstractRepository):
    """Adaptor for SQLAlchemy Repository

    Example
    -------
    >>> from freekick.datastore import DEFAULT_ENGINE
    >>> from sqlalchemy.orm import Session
    >>> from freekick.datastore.model import Team
    >>> from freekick.datastore.repository import SQLAlchemyRepository

    >>> session = Session(DEFAULT_ENGINE)
    >>> repo = SQLAlchemyRepository(session)
    >>> statement = select(Team).where(Team.code=='ARS').where(Team.league=='epl')
    >>> entity = repo.session.scalars(statement).one()
    >>> entity
    Team(code='ARS', name='Arsenal', league='epl')
    >>> entity.id
    1
    >>>
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity: Any, reference: Any) -> Any:
        return self.session.get(entity=entity, ident=reference)

    def add(self, instance: Any) -> None:
        self.session.add(instance=instance)

    def commit(self) -> None:
        self.session.commit()


class MockRepository(AbstractRepository):
    def __init__(self) -> None:
        pass

    def get(self, entity: Any, reference: Any) -> Any:
        pass

    def add(self, instance: Any) -> None:
        pass

    def commit(self) -> None:
        pass
