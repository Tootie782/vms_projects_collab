from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text, update
from sqlalchemy.orm import Session
from variamos_security import has_permissions, ResponseModel
from typing import Optional, Any
import logging

from src.db_connector import get_db
from src.model.modelDB import Project

logger = logging.getLogger(__name__)
class ModelDTO(BaseModel):
    id: str
    projectId: str
    projectName: Optional[str] = None
    engineeringType: Optional[str] = None
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    owners: Optional[list[Any]] = None

    model_config = {"from_attributes": True}

router = APIRouter(
    prefix="/v1/admin/models",
    tags=["Models", "Admin", "V1"],
)

@router.get("", dependencies=[Depends(has_permissions(["admin::models::query"]))])
def get_models(
    name: Optional[str] = Query(None),
    engineering_type: Optional[str] = Query(None, alias="engineeringType"),
    page_number: int = Query(1, alias="pageNumber"), 
    page_size: int = Query(20, alias="pageSize"),
    db: Session = Depends(get_db)
):
    types = [engineering_type] if engineering_type else ['domainEngineering', 'applicationEngineering']

    if name is not None:
        name = f"%{name}%"

    sql = text(f"""
        SELECT count(1)
        FROM variamos.project,
        jsonb_array_elements(project::jsonb->'productLines') AS productLine,
        jsonb_each(productLine) AS engineering(engineering_type, engineering_value),
        jsonb_array_elements(engineering_value->'models') AS model
        WHERE (:name IS NULL 
               OR model->>'name' ILIKE :name
               OR project.name ILIKE :name
            )
            AND engineering_type = ANY(:types)
    """)

    count_result = db.execute(sql, {"name": name, "types": types}).first()[0]
    
    sql = text(f"""
        SELECT
            project.id AS project_id,
            project.name AS project_name,
            engineering_type AS engineering_type,
            model->>'id' AS id,
            model->>'name' AS name,
            model->>'type' AS type,
            model->>'description' AS description,
            model->>'author' AS author,
            model->>'source' AS source,
            (
            SELECT json_agg(
                json_build_object(
                'id', u.id,
                'name', u.name,
                'email', u.email
                )
            )
                FROM variamos.user_project AS up
                INNER JOIN variamos.user AS u ON up.user_id = u.id
            WHERE up.project_id = project.id
            ) as owners
        FROM variamos.project,
            jsonb_array_elements(project::jsonb->'productLines') AS productLine,
            jsonb_each(productLine) AS engineering(engineering_type, engineering_value),
            jsonb_array_elements(engineering_value->'models') AS model
        WHERE (:name IS NULL 
               OR model->>'name' ILIKE :name
               OR project.name ILIKE :name
            )
            AND engineering_type = ANY(:types)
        LIMIT :limit OFFSET :offset
    """)

    offset = (page_number - 1) * page_size

    result = db.execute(sql, {"name": name, "types": types, "offset": offset, "limit": page_size}).fetchall()

    models = [
        ModelDTO(
            id=row[3],
            projectId=row[0],
            projectName=row[1],
            engineeringType=row[2],
            name=row[4],
            type=row[5],
            description=row[6],
            author=row[7],
            source=row[8],
            owners=row[9],
        )
        for row in result
    ]
    
    return ResponseModel( transactionId="ModelsAdminQuery", totalCount=count_result, data=models)

@router.put("/{model_id}", dependencies=[Depends(has_permissions(["admin::models::update"]))])
def update_model(model_id: str, model: ModelDTO, db: Session = Depends(get_db)):
    model.id = model_id
    project_id = model.projectId
    db_project = db.query(Project).filter(Project.id == project_id).first()

    if not db_project:
        return ResponseModel( transactionId="ProjectsAdminUpdate", errorCode=404, message="Project not found")
    
    updatedModel = update_model(db_project, model)

    if not updatedModel:
        return ResponseModel( transactionId="ProjectsAdminUpdate", errorCode=404, message="Model not found")
    
    stmt = (
        update(Project)
        .where(Project.id == project_id)
        .values(project=db_project.project)
    )
    db.execute(stmt)
    db.commit()

    return ResponseModel( transactionId="ProjectsAdminUpdate", data=model)

def update_model(db_project: Project, model_dto: ModelDTO):
    product_lines = db_project.project.get("productLines", [])
    model_id = model_dto.id

    for product_line in product_lines:
        if not product_line:
            continue

        domain_models = product_line.get("domainEngineering", {}).get("models", [])

        for model in domain_models:
            if not model or model.get("id") != model_id:
                continue

            model["name"] = model_dto.name
            model["author"] = model_dto.author
            model["source"] = model_dto.source
            model["description"] = model_dto.description

            return model

        application_models = product_line.get("applicationEngineering", {}).get("models", [])

        for model in application_models:
            if not model or model.get("id") != model_id:
                continue

            model["name"] = model_dto.name
            model["author"] = model_dto.author
            model["source"] = model_dto.source
            model["description"] = model_dto.description
            
            return model
        
    return None

@router.delete("/{model_id}", dependencies=[Depends(has_permissions(["admin::models::delete"]))])
def delete_model():
    return {"message": "Model deleted"}