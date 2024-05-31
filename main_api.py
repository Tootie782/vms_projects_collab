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
import logging

# Obtener el logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(levelprefix)s %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

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
    "https://app.variamos.com/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/version")
async def getVersion():
    return {"transactionId": "1", "message": "vms_projects 1.24.04.14.16"}

@app.get("/testdb")
async def testDb():
    return project_DAO.get_template_projects()

@app.post("/token")
def generate_token(request: TokenRequest, db: Session = Depends(get_db)):
    user_dao = UserDao(db)
    user = user_dao.get_by_id(str(request.user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token_data = {"sub": str(user.id)}  # Asegúrate de convertir user.id a cadena si es necesario
    secret_key, algorithm = obtener_credenciales_token()
    token = jwt.encode(token_data, secret_key, algorithm=algorithm)
    return {"transactionId": "1", "message": "Ok", "data": { "access_token": token, "token_type": "bearer"}}


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
    print("Se está inicializando la conexión con la base de datos")
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
async def guardar_modelo(project_dict: dict, template : bool, user_id: str = Depends(get_current_user)):
    print("intento guardar modelo")
    if not project_DAO.check_project_exists(user_id, project_dict):
        print("project id is none")
        return project_DAO.create_project(project_dict, template, user_id)
    else:
        print("project is updated")
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
async def update_project_name_endpoint(project_dict: dict, user_id: str = Depends(get_current_user)):
    return project_DAO.update_project_name(project_dict)

@app.delete("/deleteProject")
async def delete_project_endpoint(project_dict: dict, user_id: str = Depends(get_current_user)):
    return project_DAO.delete_project(project_dict)

@app.post("/addConfiguration")
def add_configuration(project_id: str, config_input: ConfigurationInput, user_id: str = Depends(get_current_user)):
    try:
        return project_DAO.add_configuration(project_id, config_input.project_json, config_input.id_feature_model, config_input.config_name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deleteConfiguration")
def delete_configuration(project_id: str, model_id : str, configuration_id: str, user_id: str = Depends(get_current_user)):
    try:
        return project_DAO.delete_configuration_from_project(project_id, model_id, configuration_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getConfiguration")
def get_configuration(project_id: str, configuration_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.get_configuration(project_id, configuration_id)

@app.get("/getAllConfigurations")
def get_model_configurations(project_id: str, model_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.get_model_configurations(project_id, model_id)

@app.post("/applyConfiguration")
def apply_configuration(project_id : str, model_id : str, configuration_id: str, user_id: str = Depends(get_current_user)):
    return project_DAO.apply_configuration(project_id, model_id, configuration_id)



def obtener_credenciales_token():
    with open('credentials.json', 'r') as f:
        data = json.load(f)

    # Acceder a los datos del secret key y al algorithm
    secret_key = data[0]['token']['secret_key']
    algorithm = data[0]['token']['Algorithm']
    return secret_key, algorithm