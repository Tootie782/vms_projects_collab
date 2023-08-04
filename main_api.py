from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import List

from starlette import status

import src.model
from src.db_connector import get_db
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.model.modelDAO import UserDao, ProjectDao
import json

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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserDao.get_by_id(form_data.username)
    #user = db.query(model.User).filter(model.User.user == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    password_verified = pwd_context.verify(form_data.password, user.pwd)
    if not password_verified:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Generar el token
    token_data = {"sub": user.id}
    secret_key, algorithm = obtener_credenciales_token()
    token = jwt.encode(token_data, secret_key, algorithm=algorithm)
    return {"access_token": token, "token_type": "bearer"}

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
def obtener_credenciales_token():
    with open('credentials.json', 'r') as f:
        data = json.load(f)

    # Acceder a los datos del secret key y al algorithm
    secret_key = data[1]['token']['secret_key']
    algorithm = data[1]['token']['Algorithm']
    return secret_key, algorithm