from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import List

from starlette import status

import src.model
import uuid
from fastapi import Body
from src.db_connector import get_db, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.model.modelDAO import UserDao, ProjectDao
import json
from pydantic import BaseModel

from src.model.modelDB import Project


class TokenRequest(BaseModel):
    user_id: uuid.UUID


class ShareProjectInput(BaseModel):
    user_id: str
    project_id: str

class ConfigurationInput(BaseModel):
    project_json: dict
    id_feature_model: str
    config_name: str

app = FastAPI()
origins = [
    "*",
    "https://variamos2024.azurewebsites.net/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/token")
def generate_token(request: TokenRequest, db: Session = Depends(get_db)):
    user_dao = UserDao(db)
    user = user_dao.get_by_id(str(request.user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token_data = {"sub": str(user.id)}  # Asegúrate de convertir user.id a cadena si es necesario
    secret_key, algorithm = obtener_credenciales_token()
    token = jwt.encode(token_data, secret_key, algorithm=algorithm)
    return {"transactionId": "1", "message": "Ok", "data": {"access_token": token, "token_type": "bearer"}}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # actualiza esto con la URL de tu endpoint de autenticación


def get_current_user(token: str = Depends(oauth2_scheme)):
    secret_key, algorithm = obtener_credenciales_token()

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise Exception("El usuario no existe")
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.on_event("startup")
async def iniciar_app():
    db = SessionLocal()
    global user_DAO
    global project_DAO
    user_DAO = UserDao(db)
    project_DAO = ProjectDao(db)


@app.on_event("shutdown")
def shutdown_event():
    close_db()


def close_db():
    db = SessionLocal()  # Aquí obtienes la sesión
    db.close()


@app.post("/saveProject")
async def guardar_modelo(project_dict: dict, user_id: str = Depends(get_current_user)):
    if project_dict.get("id") is None:
        return project_DAO.create_project(project_dict, user_id)
    else:
        return project_DAO.update_project(project_dict, user_id)


@app.get("/getProjects")
async def obtener_modelos(user_id: str = Depends(get_current_user)):
    return user_DAO.get_projects(user_id)


@app.get("/getTemplateProjects")
async def obtener_modelos_template(user_id: str = Depends(get_current_user)):
    return project_DAO.get_template_projects()


@app.get("/getProject")
async def obtener_modelo(project_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.get_by_id(project_id)


@app.post("/shareProject")
async def compartir_modelo(data: ShareProjectInput, to_username: str = Depends(get_current_user)):
    return project_DAO.share_project(data.project_id, data.user_id)


@app.get("/usersProject")
async def obtener_usuarios_proyecto(project_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.get_users(project_id, user_id)


@app.get("/findUser")
async def buscar_usuario_email(user_mail: str, db: Session = Depends(get_db)):
    return user_DAO.get_by_email(user_mail)


@app.get("/permissionProject")
async def obtener_permisos(project_id: str, db: Session = Depends(get_db)):
    return None

@app.put("/updateProjectName")
async def update_project_name_endpoint(project_id: str, new_name: str, user_id: str = Depends(get_current_user)):
    return project_DAO.update_project_name(project_id, new_name)

@app.delete("/deleteProject")
async def delete_project_endpoint(project_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.delete_project(project_id)

@app.post("/addConfiguration")
def add_configuration(project_id: str, config_input: ConfigurationInput, db: Session = Depends(get_db)):
    project_dao = ProjectDao(db)
    try:
        return project_dao.add_configuration(project_id, config_input.project_json, config_input.id_feature_model, config_input.config_name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deleteConfiguration")
def delete_configuration(project_id: str, configuration_id: str, db: Session = Depends(get_db)):
    project_dao = ProjectDao(db)
    try:
        return project_dao.delete_configuration_from_project(db, project_id, configuration_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getConfiguration")
def get_configuration(project_id: str, configuration_id: str, db: Session = Depends(get_db)):
    project_dao = ProjectDao(db)
    try:
        project = project_dao.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Buscar la configuración específica
        for config in project.configuration['configurations']:
            if config['id'] == configuration_id:
                return {"transactionId": "1", "message": "Configuration found", "data": config}

        raise HTTPException(status_code=404, detail="Configuration not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getAllConfigurations")
def get_all_configurations(project_id: str, db: Session = Depends(get_db)):
    project_dao = ProjectDao(db)
    try:
        project = project_dao.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Verificar si el proyecto tiene configuraciones almacenadas
        if not project.configuration or 'configurations' not in project.configuration:
            return {"transactionId": "1", "message": "No configurations available", "data": []}

        # Retornar todas las configuraciones encontradas
        return {"transactionId": "1", "message": "Configurations retrieved successfully", "data": project.configuration['configurations']}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/applyConfiguration")
def apply_configuration(model_json: dict, configuration: dict):
    try:
        # Crear un diccionario de las características con sus valores configurados
        feature_values = {feature['id']: feature['value'] for feature in configuration['features']}
        for product_line in model_json['productLines']:
            for model in product_line['domainEngineering']['models']:
                for element in model['elements']:
                    if element['id'] in feature_values:
                        for prop in element['properties']:
                            if prop['name'] == 'Selected':
                                prop['value'] = feature_values[element['id']]

        return {"transactionId": "1", "message": "Configuration applied successfully", "data": model_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# saber usuarios autorizados para ver modelos
def obtener_credenciales_token():
    with open('credentials.json', 'r') as f:
        data = json.load(f)

    # Acceder a los datos del secret key y al algorithm
    secret_key = data[1]['token']['secret_key']
    algorithm = data[1]['token']['Algorithm']
    return secret_key, algorithm