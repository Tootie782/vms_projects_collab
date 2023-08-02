from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import List

from starlette import status

import src.model
from src.db_connector import get_db
from fastapi.middleware.cors import CORSMiddleware

from src.model.modelDAO import UserDao, ProjectDao

app = FastAPI()
origins = [
    "https://variamos2023.azurewebsites.net/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # actualiza esto con la URL de tu endpoint de autenticación

def get_current_user(token: str = Depends(oauth2_scheme)):
    SECRET_KEY = "secret_key"  # clave secreta para verificar el JWT
    ALGORITHM = "HS256"  # el algoritmo que usas para codificar el JWT

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    db = Depends(get_db)
    global user_DAO
    global project_DAO
    user_DAO = UserDao(db)
    project_DAO = ProjectDao(db)

@app.post("/saveproject")
async def guardar_modelo(project: dict, user_id: int = Depends(get_current_user)):
    return project_DAO.create_project(project,user_id)

@app.get("/getProjects")
async def obtener_modelos(user_id: int = Depends(get_current_user)):
    return user_DAO.get_projects(user_id)


#modificar
@app.get("/getProject/{project_id}")
async def obtener_modelo(project_id : int, user_id: int = Depends(get_current_user)):
    return project_DAO.get_by_id(project_id)

@app.get("/shareproject/{project_id}/{user_id}")
async def compartir_modelo(user_id : int, project_id : int, to_username: int = Depends(get_current_user)):
    return project_DAO.share_project(project_id,user_id)

@app.get("/usersproject/{project_id}")
async def obtener_usuarios_proyecto(project_id : int, user_id: int = Depends(get_current_user)):
    return project_DAO.get_users(project_id)

@app.get("/finduser")
async def buscar_usuario_email(project_id : int, db: Session = Depends(get_db)):
    return None

@app.get("/permissionproject")
async def obtener_permisos(project_id : int, db: Session = Depends(get_db)):
    return None

#saber usuarios autorizados para ver modelos
