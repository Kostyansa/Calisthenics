from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy import select

from config.engine import InternalDatabaseConfiguration
from entity import User


class UserRepository:
    __slots__ = "engine"
    instance = None

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls(InternalDatabaseConfiguration.get_engine())
        return cls.instance

    def save(self, user: User):
        with Session(self.engine, expire_on_commit=False) as session:
            session.add(user)
            session.commit()

    def get_all(self):
        with Session(self.engine) as session:
            statement = select(User)
            users = session.scalars(statement).all()
            session.expunge_all()
            return users
