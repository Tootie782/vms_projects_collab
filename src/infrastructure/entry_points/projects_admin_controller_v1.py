from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.orm import Session
from variamos_security import has_permissions, ResponseModel
from typing import Optional, Any
from datetime import datetime

from src.db_connector import get_db
from src.model.modelDB import Project

class ProjectDTO(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    project: Optional[Any] = None
    author: Optional[str] = None
    source: Optional[str] = None
    date: Optional[datetime] = None
    template: Optional[bool] = None

    model_config = {"from_attributes": True}


router = APIRouter(
    prefix="/v1/admin/projects",
    tags=["Projects", "Admin", "V1"],
)

@router.get("", dependencies=[Depends(has_permissions(["admin::projects::query"]))])
def get_projects(
    name: Optional[str] = Query(None), 
    is_template: Optional[bool] = Query(None, alias="isTemplate"), 
    page_number: int = Query(1, alias="pageNumber"), 
    page_size: int = Query(20, alias="pageSize"),
    db: Session = Depends(get_db)
):
    query = db.query(
        Project.id, Project.name, Project.description, Project.author, Project.source, Project.date, Project.template, Project.project
    )

    if name is not None:
        query = query.filter(Project.name.ilike(f"%{name}%"))

    if is_template is not None:
        query = query.filter(Project.template == is_template)

    total = query.count()
    projects = query.offset((page_number - 1) * page_size).limit(page_size).all()

    return ResponseModel( transactionId="ProjectsAdminQuery", totalCount=total, data=[ProjectDTO.model_validate(project) for project in projects])

@router.put("/{project_id}", dependencies=[Depends(has_permissions(["admin::projects::update"]))])
def update_project(project_id: str, project: ProjectDTO, db: Session = Depends(get_db)):
    dbProject = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return ResponseModel( transactionId="ProjectsAdminUpdate", errorCode=404, message="Project not found")

    dbProject.name = project.name
    dbProject.template = project.template
    dbProject.author = project.author
    dbProject.description = project.description
    dbProject.source = project.source

    db.commit()
    db.refresh(dbProject)

    return ResponseModel( transactionId="ProjectsAdminUpdate", data=ProjectDTO.model_validate(dbProject))

@router.delete("/{project_id}", dependencies=[Depends(has_permissions(["admin::projects::delete"]))])
def delete_project(project_id: str, db: Session = Depends(get_db)):
    stmt = delete(Project).where(Project.id == project_id)

    db.execute(stmt)
    db.commit()

    return ResponseModel( transactionId="ProjectsAdminDelete")