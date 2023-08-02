from sqlalchemy.orm import Session
import model  # Asegúrate de importar tus modelos aquí


class UserDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(model.User).filter(model.User.id == user_id).first()

    def get_projects(self, user_id: int):
        return self.db.query(model.UserProject).filter(model.UserProject.user_id == user_id).all()


class ProjectDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int):
        return self.db.query(model.Project).filter(model.Project.id == project_id).first()

    def create_project(self, project: model.Project, user_id: int, data : dict):
        project = model.Project(data=data)
        self.db.add(project)
        # Crea una nueva entrada en la tabla UserProject para asociar el proyecto con el usuario
        user_project = model.UserProject(user_id=user_id, project_id=project.id)
        self.db.add(user_project)
        self.db.commit()
        return user_project
