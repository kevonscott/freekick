import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from freekick.database.model import Base, Team
from freekick.database.repository import SQLAlchemyRepository
from freekick.database.util import DBUtils

STMT = """
INSERT INTO team (code, name, league)
VALUES ('T1', 'Team1', 'League1'), ('T2', 'Team2', 'League1')
"""


class DBUtilsTestcase(unittest.TestCase):
    def setUp(self) -> None:
        # In-memory database. Also echo for each query
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        Base.metadata.create_all(bind=self.engine)  # create the tables
        self.repository = SQLAlchemyRepository(session=Session(self.engine))

        # Insert some sample data
        self.repository.session.execute(statement=text(STMT))

    def test_get_team_code_str(self):
        team2_code = DBUtils.get_team_code(
            repository=self.repository,
            league="League1",
            team_name="Team2",
            code_type="str",
        )
        self.assertEqual(team2_code, "T2")

    def test_get_team_code_int(self):
        team2_code_int = DBUtils.get_team_code(
            repository=self.repository,
            league="League1",
            team_name="Team2",
            code_type="int",
            team_code="T2",
        )
        self.assertEqual(team2_code_int, 2)


class SQLAlchemyRepositoryTestcase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        Base.metadata.create_all(bind=self.engine)  # create the tables
        self.repository = SQLAlchemyRepository(session=Session(self.engine))

        # Insert some sample data
        self.repository.session.execute(statement=text(STMT))

    def test_get(self):
        res = self.repository.get(Team, 1)  # First instance should be T1

        self.assertEqual(res.id, 1)
        self.assertEqual(res.code, "T1")
        self.assertEqual(res.name, "Team1")

    def test_add(self):
        t9999 = Team(code="T9999", name="Team9999", league="League9999")
        self.repository.add(t9999)
        self.repository.commit()

        stmt = text(
            """
        SELECT id, code, name, league FROM team WHERE code='T9999'
        """
        )
        id, code, name, league = self.repository.session.execute(stmt).one()

        self.assertEqual(id, t9999.id)
        self.assertEqual(code, t9999.code)
        self.assertEqual(name, t9999.name)
        self.assertEqual(league, t9999.league)
