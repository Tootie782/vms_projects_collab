from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select, and_, exists, cast, String
from sqlalchemy.sql import func
from .modelDB import User, Project, user_project_association
from fastapi.responses import JSONResponse
from datetime import datetime
from ..utils.configurationManager import manage_configurations
import json


class UserDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        self.db.close()
        return user

    # def get_projectsOld(self, user_id: str):
    #     # Primero, busquemos todos los project_ids asociados al user_id
    #     stmt = select(user_project_association.c.project_id).where(user_project_association.c.user_id == user_id)
    #     result = self.db.execute(stmt).fetchall()
    #     project_ids = [row.project_id for row in result]
    #     projects = self.db.query(Project).filter(Project.id.in_(project_ids)).all()
    #     projects_list = [project.project for project in projects]
    #     self.db.close()
    #     return {"projects": projects_list}

    def get_projects(self, user_id: str):
        # Primero, busquemos todos los project_ids asociados al user_id
        stmt = select(user_project_association.c.project_id).where(user_project_association.c.user_id == user_id)
        result = self.db.execute(stmt).fetchall()
        project_ids = [row.project_id for row in result]
        projects = self.db.query(Project).filter(Project.id.in_(project_ids)).all()
        self.db.close()

        records = []
        for project in projects:
            records.append({"id":  project.id, "name": project.name, "template": project.template}) 
        return {"transactionId": "1", "message": "Ok", "data": { "projects": records}}

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

    def delete_project(self,user_id: str, project_id: str):
        user = self.get_by_id(user_id)
        if user:
            for project in user.projects:
                if project.id == project_id:
                    return project
        return None

class ProjectDao:
    def __init__(self, db: Session):
        self.db = db

    def check_project_exists(self, user_id: str, project_json: dict) -> bool:
        project_json_str = json.dumps(project_json, sort_keys=True)
        project_exists = self.db.query(exists().where(
            and_(
                func.cast(Project.project, String) == project_json_str,
                user_project_association.c.user_id == user_id,
                user_project_association.c.project_id == Project.id
            )
        )).scalar()
        return project_exists

    def get_by_id(self, project_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        self.db.close()
        return {"transactionId": "1", "message": "Ok", "data": {"project": project}}

    """
    def get_all_configurations(self, project_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        try:
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            if not project.configuration or 'configurations' not in project.configuration:
                return {"transactionId": "1", "message": "No configurations available", "data": []}
            return {"transactionId": "1", "message": "Configurations retrieved successfully",
                    "data": project.configuration['configurations']}
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_configuration(self, project_id: str, configuration_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        try:
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            for config in project.configuration['configurations']:
                if config['id'] == configuration_id:
                    return {"transactionId": "1", "message": "Configuration found", "data": config}

            raise HTTPException(status_code=404, detail="Configuration not found")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def apply_configuration(self, project_id, configuration_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project_data = project.project
        configurations = project.configuration.get("configurations", [])
        configuration = next((config for config in configurations if config["id"] == configuration_id), None)
        if not configuration:
            raise HTTPException(status_code=404, detail="Configuration not found")
        try:
            feature_values = {feature['id']: feature['properties'] for feature in configuration['features']}

            # Aplicar los valores de configuración a las propiedades del proyecto
            for product_line in project_data['productLines']:
                for model in product_line['domainEngineering']['models']:
                    for element in model['elements']:
                        if element['id'] in feature_values:
                            for prop in element['properties']:
                                    prop['properties'] = feature_values[element['id']]

            return {"transactionId": "1", "message": "Configuration applied successfully", "data": project_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    """

    def apply_configuration(self, project_id, model_id, configuration_id: str):
        # Recuperar el proyecto
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Verificar y extraer las configuraciones del modelo especificado
        model_configurations = project.configuration.get('modelConfigurations', {}).get(model_id, [])
        configuration = next((config for config in model_configurations if config['id'] == configuration_id), None)
        if not configuration:
            raise HTTPException(status_code=404, detail="Configuration not found")

        try:
            # Construir un diccionario de los valores de las características configuradas
            feature_values = {}
            for feature in configuration['features']:
                for prop in feature.get('properties', []):
                    if 'id' in prop and 'value' in prop:
                        feature_values[prop['id']] = prop['value']

            # Aplicar la configuración a las características del modelo especificado
            for product_line in project.project['productLines']:
                for model in product_line['domainEngineering']['models']:
                    if model['id'] == model_id:
                        for element in model['elements']:
                            for prop in element.get('properties', []):
                                if prop['id'] in feature_values:
                                    prop['value'] = feature_values[prop['id']]

            # Devolver el proyecto modificado como JSON sin modificar la base de datos
            return {"transactionId": "1", "message": "Configuration applied successfully", "data": project.project}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_configuration(self, project_id: str, configuration_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        for model_configs in project.configuration.get('modelConfigurations', {}).values():
            for config in model_configs:
                if config['id'] == configuration_id:
                    return {"transactionId": "1", "message": "Configuration found", "data": config}

        raise HTTPException(status_code=404, detail="Configuration not found")

    def get_model_configurations(self, project_id: str, model_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if 'modelConfigurations' not in project.configuration:
            return {"transactionId": "1", "message": "No configurations available", "data": []}

        model_configs = project.configuration['modelConfigurations'].get(model_id, [])
        if not model_configs:
            return {"transactionId": "1", "message": "No configurations available for the specified model", "data": []}

        return {"transactionId": "1", "message": "Configurations retrieved successfully", "data": model_configs}

    def get_template_projects(self):
        projects = self.db.query(Project).filter(Project.template == True).all()
        self.db.close()
        records = []
        for project in projects:
            records.append({"id":  project.id, "name": project.name, "template": project.template}) 
        return {"transactionId": "1", "message": "Ok", "data": { "projects": records}}

    """
    def create_project(self, project_dict: dict, template : bool, user_id: str):
        print("creando proyecto...")
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        # Configuración inicial vacía
        initial_configuration = {
            "idModel": str(uuid4()),
            "nameApplication": project_dict.get("name"),  # Tomando el nombre del proyecto como nombre de la aplicación
            "configurations": []
        }
        #id = str(uuid4())
        project = Project(id=str(uuid4()), name=project_dict.get("name"), project=project_dict,
                          template=template, configuration=initial_configuration)
        self.db.add(project)
        self.db.flush()  # Obtener el ID de proyecto recién creado antes de commitear
        # Asociar el proyecto con el usuario en la tabla de asociación
        assoc = user_project_association.insert().values(user_id=user_id, project_id=project.id)
        self.db.execute(assoc)
        self.db.commit()
        print("proyecto creado")
        content = {"transactionId": "1", "message": "Project created successfully", "data": {"id": project.id}}
        self.db.close()
        return JSONResponse(content=content, status_code=200)
    """


    def create_project(self, project_dict: dict, name : str, template: bool, description: str, source: str,  author: str, user_id: str):
        print("creando proyecto...")
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        initial_configuration = {  # Lista de configuraciones ahora por modelID
        }
        project = Project(id=str(uuid4()), name=name, project=project_dict,
                          template=template, configuration=initial_configuration,description=description, source=source, author=author, date= datetime.now())
        self.db.add(project)
        self.db.flush()  # Obtener el ID de proyecto recién creado antes de commitear
        # Asociar el proyecto con el usuario en la tabla de asociación
        assoc = user_project_association.insert().values(user_id=user_id, project_id=project.id)
        self.db.execute(assoc)
        self.db.commit()
        print("proyecto creado")
        content = {"transactionId": "1", "message": "Project created successfully", "data": {"id": project.id}}
        self.db.close()
        return JSONResponse(content=content, status_code=200)

    def update_project(self, project_dict: dict, name : str, template: bool, description: str, source: str,  author: str, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        current_date = datetime.now()
        project = self.db.query(Project).filter(Project.project == project_dict).first()
        if not project:
            self.db.close()
            raise Exception("El proyecto no existe")
        project.name = name
        project.template = template
        project.description = description
        project.source = source
        project.author = author
        project.date = current_date
        self.db.commit()
        content = {"transactionId": "1", "message": "Project updated successfully", "data": {"id": id}}
        self.db.close()
        return JSONResponse(content=content, status_code=200)

    def update_project_name(self, project_dict: dict):
        id=project_dict.get("id")
        project=Project(id=id, name=project_dict.get("name"), project=project_dict.get("project"), template=project_dict.get("template"))
        self.db.query(Project).filter(Project.id == project.id).update({"name": project.name})     
        self.db.commit()
        self.db.close()
        content = {"transactionId": "1", "message": "Project name updated successfully"}
        return JSONResponse(content=content, status_code=200)

    def add_configuration(self, project_id: str, project_json : dict, id_feature_model, config_name : str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            self.db.close()
            raise HTTPException(status_code=404, detail="Project not found")
        if 'configuration' not in project.project or project.project['configuration'] is None:
            project.project['configuration'] = {}

        project.configuration= manage_configurations(project_json, id_feature_model, config_name, project.configuration)
        print("project configuration: ")
        print(project.configuration)
        flag_modified(project, "configuration")
        self.db.commit()
        content = {"transactionId": "1", "message": "Project name updated successfully"}
        self.db.close()
        return JSONResponse(content=content, status_code=200)

    """
    def delete_configuration_from_project(self, project_id: str, configuration_id: str):
        # Buscar el proyecto por ID
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Asegurarse de que el proyecto tiene configuraciones
        if not project.configuration or 'configurations' not in project.configuration:
            raise HTTPException(status_code=404, detail="No configurations found in project")

        # Filtrar la configuración que se desea eliminar
        original_count = len(project.configuration['configurations'])
        project.configuration['configurations'] = [
            config for config in project.configuration['configurations'] if config['id'] != configuration_id
        ]

        # Verificar si se eliminó alguna configuración
        if original_count == len(project.configuration['configurations']):
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Guardar los cambios en la base de datos
        flag_modified(project, "configuration")
        self.db.commit()
        content = {"transactionId": "1", "message": "Project deleted successfully"}
        return JSONResponse(content=content, status_code=200)
        """

    def delete_configuration_from_project(self, project_id: str, model_id: str, configuration_id: str):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        model_configurations = project.configuration.get('modelConfigurations', {}).get(model_id, [])
        original_count = len(model_configurations)
        updated_configurations = [config for config in model_configurations if config['id'] != configuration_id]

        if len(updated_configurations) == original_count:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Update the configurations for the specific model
        project.configuration['modelConfigurations'][model_id] = updated_configurations
        flag_modified(project, "configuration")  # Mark the 'configuration' attribute as modified
        self.db.commit()
        content = {"transactionId": "1", "message": "Configuration deleted successfully"}
        self.db.close()
        return JSONResponse(content=content, status_code=200)

    def delete_project(self, project_dict: dict):
        id=project_dict.get("id")
        project = self.db.query(Project).filter(Project.id == id).first()
        if not project:
            self.db.close()
            raise Exception("Project not found")
        self.db.delete(project)
        self.db.commit()
        content = {"transactionId": "1", "message": "Project deleted successfully", "data": {"id": project_id}}
        self.db.close()
        return JSONResponse(content=content, status_code=200)

    def share_project(self, project_id: str, to_username: str):
        user = self.db.query(User).filter(User.id == to_username).first()
        if not user:
            self.db.close()
            raise Exception("El usuario no existe")
        # Verificar ya está compartido con el usuario
        assoc_exists = self.db.execute(select(user_project_association)
                                       .where(and_(user_project_association.c.user_id == user.id,
                                                   user_project_association.c.project_id == project_id))).fetchone()
        if not assoc_exists:
            assoc = user_project_association.insert().values(user_id=user.id, project_id=project_id)
            self.db.execute(assoc)
        self.db.commit()
        self.db.close()
        return JSONResponse(content={"message": "Project shared successfully"},
                            status_code=200)

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
        return {"users": users_list}


