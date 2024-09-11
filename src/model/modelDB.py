from uuid import uuid4

from sqlalchemy import Boolean, Table, Column, ForeignKey, Integer, String, JSON, MetaData
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData(schema="variamos")
# Tabla de asociación
class Project(Base):
    __tablename__ = 'project'
    __table_args__ = {'schema': 'variamos'}

    id = Column(String, primary_key=True)
    project = Column(JSON)
    name = Column(String)
    template = Column(Boolean)
    configuration = Column(JSON,  nullable=True)
    description = Column(String,  nullable=True)
    source = Column(String,  nullable=True)
    author = Column(String,  nullable=True)
    date = Column(DateTime,  nullable=True)
    type_models = Column(String, nullable=True)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'variamos'}

    id = Column(String, primary_key=True, default=str(uuid4()))
    user = Column(String)
    name = Column(String)
    email = Column(String)


user_project_association = Table(
    'user_project', metadata,
    Column('user_id', String, ForeignKey('variamos.user.id'), primary_key=True),
    Column('project_id', String, ForeignKey('variamos.project.id'), primary_key=True)
)


