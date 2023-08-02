from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import model
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


@app.on_event("startup")
async def iniciar_app():
    db = Depends(get_db)
    global user_DAO
    global project_DAO
    user_DAO = UserDao(db)
    project_DAO = ProjectDao(db)

@app.post("/saveproject")
async def guardar_modelo(user_id: int, project: dict):
    return project_DAO.create_project(project,user_id)

@app.get("/getProjects")
async def obtener_modelos(user_id : int, db: Session = Depends(get_db)):
    return user_DAO.get_projects(user_id)

@app.get("/getProject")
async def obtener_modelo(project_id : int, db: Session = Depends(get_db)):
    return project_DAO.get_by_id(project_id)

@app.get("/shareproject")
async def compartir_modelo(user_id : int, project_id : int, db: Session = Depends(get_db)):
    return project_DAO.share_project(project_id,user_id)

@app.get("/usersproject")
async def obtener_usuarios_proyecto(project_id : int, db: Session = Depends(get_db)):
    return project_DAO.get_users(project_id)

@app.get("/finduser")
async def buscar_usuario_email(project_id : int, db: Session = Depends(get_db)):
    return None

@app.get("/permissionproject")
async def obtener_permisos(project_id : int, db: Session = Depends(get_db)):
    return None

#saber usuarios autorizados para ver modelos
