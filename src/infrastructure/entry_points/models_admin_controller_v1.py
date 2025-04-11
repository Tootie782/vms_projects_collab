from fastapi import APIRouter, Depends
from variamos_security import has_permissions

router = APIRouter(
    prefix="/v1/admin/models",
    tags=["Models", "Admin", "V1"],
)

@router.get("/", dependencies=[Depends(has_permissions(["admin::models::query"]))])
def get_models():
    return {"message": "List of models"}

@router.put("/{project_id}", dependencies=[Depends(has_permissions(["admin::models::update"]))])
def update_model():
    return {"message": "Model update"}

@router.delete("/{project_id}", dependencies=[Depends(has_permissions(["admin::models::delete"]))])
def delete_model():
    return {"message": "Model deleted"}