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

    def get_by_email(self, email: str):
        user = self.db.query(User).filter(User.email == email).first()
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

    def create_project(self, project_data: dict, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        project = Project(project=project_data)
        self.db.add(project)
        self.db.flush()  # Obtener el ID de proyecto recién creado antes de commitear
        # Asociar el proyecto con el usuario en la tabla de asociación
        assoc = user_project_association.insert().values(user_id=user_id, project_id=project.id)
        self.db.execute(assoc)
        self.db.commit()
        self.db.close()
        return project

    def share_project(self, project_id: str, to_username: str):
        user = self.db.query(User).filter(User.id == to_username).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        #Verificar ya está compartido con el usuario
        assoc_exists = self.db.execute(select(user_project_association)
                                       .where(and_(user_project_association.c.user_id == user.id,
                                                   user_project_association.c.project_id == project_id))).fetchone()
        if not assoc_exists:
            assoc = user_project_association.insert().values(user_id=user.id, project_id=project_id)
            self.db.execute(assoc)
        self.db.commit()
        self.db.close()
        return project_id

    def get_users(self, project_id: str, requesting_user_id: str):
        is_user_associated = self.db.query(user_project_association).filter(
            and_(
                user_project_association.c.project_id == project_id,
                user_project_association.c.user_id == requesting_user_id
            )
        ).first()
        if not is_user_associated:
            self.db.close()
            raise Exception("El usuario no tiene permiso para ver los usuarios de este proyecto.")
        stmt = select(user_project_association.c.user_id).where(user_project_association.c.project_id == project_id)
        result = self.db.execute(stmt).fetchall()
        user_ids = [row.user_id for row in result]
        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        users_list = [{"id": user.id, "username": user.user, "name": user.name, "email": user.email} for user in users]
        self.db.close()
        return users_list
