from sqlalchemy.orm import Session
from .modelDB import User
from .modelDB import Project
#import model  # Asegúrate de importar tus modelos aquí


class UserDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_projects(self, user_id: str):
        user = self.get_by_id(user_id)
        return user.projects if user else []

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.user == username).first()

    def get_specific_project(self, user_id: str, project_id: str):
        user = self.get_by_id(user_id)
        if user:
            for project in user.projects:
                if project.id == project_id:
                    return project
        return None
class ProjectDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: str):
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create_project(self, project: Project, user_id: str, data: dict):
        project = Project(data=data)
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.projects.append(project)
        self.db.add(project)
        self.db.commit()
        return project

    def share_project(self, project_id: str, to_username: str):
        project = self.get_by_id(project_id)
        user = self.db.query(User).filter(User.user == to_username).first()
        if not user:
            raise Exception("El usuario no existe")
        if project not in user.projects:
            user.projects.append(project)
        self.db.commit()
        return project

    def get_users(self, project_id: int):
        project = self.get_by_id(project_id)
        return project.users if project else []