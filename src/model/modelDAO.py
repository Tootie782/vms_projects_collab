from sqlalchemy.orm import Session
import model  # Asegúrate de importar tus modelos aquí


class UserDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(model.User).filter(model.User.id == user_id).first()

    def get_projects(self, user_id: int):
        return self.db.query(model.UserProject).filter(model.UserProject.user_id == user_id).all()

    def get_by_username(self, username: str):
        return self.db.query(model.User).filter(model.User.user == username).first()

    def get_specific_project(self, user_id: int, project_id: int):
        return self.db.query(model.UserProject).filter(
            model.UserProject.user_id == user_id,
            model.UserProject.project_id == project_id).first()


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

    def share_project(self, project_id: int, to_username: str):
        user_dao = UserDao(self.db)
        to_user = user_dao.get_by_username(to_username)
        if not to_user:
            raise Exception("El usuario no existe")
        user_project = model.UserProject(user_id=to_user.id, project_id=project_id)
        self.db.add(user_project)
        self.db.commit()
        return user_project

    def get_users(self, project_id: int):
        user_projects = self.db.query(model.UserProject).filter(model.UserProject.project_id == project_id).all()
        users = []
        user_dao = UserDao(self.db)
        for user_project in user_projects:
            user = user_dao.get_by_id(user_project.user_id)
            users.append(user)
        return users
