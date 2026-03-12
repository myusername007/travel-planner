from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    PlaceCreate, PlaceUpdate, PlaceResponse,
)
from app.services import (
    create_project, list_projects, get_project,
    update_project, delete_project,
    add_place, list_places, get_place, update_place,
    ProjectNotFound, PlaceNotFound, BusinessError,
)

router = APIRouter()


# Projects

# create project
@router.post(
        "/projects", 
        response_model=ProjectResponse, 
        status_code=201, 
        tags=["Projects"]
)
async def create_project_endpoint(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_project(db, data)
    except BusinessError as e:
        raise HTTPException(status_code=422, detail=str(e))

# list all projects
@router.get(
        "/projects", 
        response_model=list[ProjectResponse], 
        tags=["Projects"]
)
async def list_projects_endpoint(db: AsyncSession = Depends(get_db)):
    return await list_projects(db)

# get project by id
@router.get(
        "/projects/{project_id}", 
        response_model=ProjectResponse, 
        tags=["Projects"]
)
async def get_project_endpoint(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_project(db, project_id)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# update project
@router.patch(
        "/projects/{project_id}", 
        response_model=ProjectResponse, 
        tags=["Projects"]
)
async def update_project_endpoint(
    project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        return await update_project(db, project_id, data)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# delete project
@router.delete(
        "/projects/{project_id}", 
        status_code=204, 
        tags=["Projects"]
)
async def delete_project_endpoint(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await delete_project(db, project_id)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessError as e:
        raise HTTPException(status_code=422, detail=str(e))


# Places 

# add a place
@router.post(
    "/projects/{project_id}/places",
    response_model=PlaceResponse,
    status_code=201,
    tags=["Places"],
)
async def add_place_endpoint(
    project_id: str, data: PlaceCreate, db: AsyncSession = Depends(get_db)
):
   
    try:
        return await add_place(db, project_id, data)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessError as e:
        raise HTTPException(status_code=422, detail=str(e))


# list all places for a project
@router.get(
    "/projects/{project_id}/places",
    response_model=list[PlaceResponse],
    tags=["Places"],
)
async def list_places_endpoint(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await list_places(db, project_id)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# get one place
@router.get(
    "/projects/{project_id}/places/{place_id}",
    response_model=PlaceResponse,
    tags=["Places"],
)
async def get_place_endpoint(
    project_id: str, place_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        return await get_place(db, project_id, place_id)
    except (ProjectNotFound, PlaceNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))


# update place
@router.patch(
    "/projects/{project_id}/places/{place_id}",
    response_model=PlaceResponse,
    tags=["Places"],
)
async def update_place_endpoint(
    project_id: str, place_id: str, data: PlaceUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        return await update_place(db, project_id, place_id, data)
    except (ProjectNotFound, PlaceNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessError as e:
        raise HTTPException(status_code=422, detail=str(e))
