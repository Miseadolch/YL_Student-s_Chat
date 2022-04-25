import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Ankets(SqlAlchemyBase):
    __tablename__ = 'ankets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    theme = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
    group = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
    opis = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
