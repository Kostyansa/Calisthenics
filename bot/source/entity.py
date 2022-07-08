import enum
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, String, JSON, Enum
from sqlalchemy.orm import declarative_base, relationship

from config.engine import InternalDatabaseConfiguration

Base = declarative_base()


class Language(enum.Enum):
    EN = 0
    RU = 1


# class Step(Base):
#     __tablename__ = "step"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#
#     step = relationship("Step")


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, primary_key=False)
    # language = Column(Enum(Language), nullable=True)

    # step_id = Column(Integer, ForeignKey("step.id"))


@dataclass
class Response:
    message: str
    replyMarkup: Optional[object] = None
    photo: Optional[object] = None


Base.metadata.create_all(InternalDatabaseConfiguration.get_engine())
