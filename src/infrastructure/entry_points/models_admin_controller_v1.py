from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from variamos_security import has_permissions, ResponseModel
from typing import Optional, Any
import logging

from src.db_connector import get_db

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

@router.put("/{project_id}", dependencies=[Depends(has_permissions(["admin::models::update"]))])
def update_model(db: Session = Depends(get_db)):
    return {"message": "Model update"}

@router.delete("/{project_id}", dependencies=[Depends(has_permissions(["admin::models::delete"]))])
def delete_model():
    return {"message": "Model deleted"}