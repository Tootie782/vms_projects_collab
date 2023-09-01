from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from .modelDB import User, Project, user_project_association


class UserDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        self.db.close()
        return user

    def get_projects(self, user_id: str):
        # Primero, busquemos todos los project_ids asociados al user_id
        stmt = select(user_project_association.c.project_id).where(user_project_association.c.user_id == user_id)
        result = self.db.execute(stmt).fetchall()
        # Extraigamos los project_ids de los resultados
        project_ids = [row.project_id for row in result]
        # Ahora, recuperemos los proyectos usando los project_ids
        projects = self.db.query(Project).filter(Project.id.in_(project_ids)).all()
        # Convertimos los objetos de proyectos a una lista de diccionarios (esto es opcional)
        projects_list = [project.project for project in projects]
        self.db.close()
        return projects_list

    def get_by_username(self, username: str):
        user = self.db.query(User).filter(User.user == username).first()
        self.db.close()
        return user

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
        project = self.db.query(Project).filter(Project.id == project_id).first()
        self.db.close()
        return project

    def create_project(self, project: Project, user_id: str, data: dict):
        project = Project(data=data)
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.projects.append(project)
        self.db.add(project)
        self.db.commit()
        self.db.close()
        return project

    def share_project(self, project_id: str, to_username: str):
        project = self.get_by_id(project_id)
        user = self.db.query(User).filter(User.user == to_username).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        if project not in user.projects:
            user.projects.append(project)
        self.db.commit()
        self.db.close()
        return project

    def get_users(self, project_id: int):
        project = self.get_by_id(project_id)
        return project.users if project else []
