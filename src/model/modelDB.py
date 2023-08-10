from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
    users = relationship("UserProject", back_populates="project")


class UserProject(Base):
    __tablename__ = "user_project"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="users")

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    pwd = Column(String)
    name = Column(String)
    projects = relationship("UserProject", back_populates="user")

