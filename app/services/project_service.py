from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Place, Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate, PlaceCreate, PlaceUpdate
from app.services.art_api import get_artwork

MAX_PLACES_PER_PROJECT = 10


class ProjectNotFound(Exception):
    pass


class PlaceNotFound(Exception):
    pass


class BusinessError(Exception):
    pass


# helpers 

async def _get_project_with_places(db: AsyncSession, project_id: str) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.places))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFound(f"Project {project_id} not found")
    return project


async def _fetch_and_validate_place(external_id: int) -> str:
    artwork = await get_artwork(external_id) # validate place exists in API and get name
    if not artwork:
        raise BusinessError(f"Place with external_id {external_id} not found in Art Institute API")
    return artwork.get("title", f"Artwork {external_id}")


async def _check_project_completion(db: AsyncSession, project: Project) -> None:
    if project.places and all(p.is_visited for p in project.places): # mark completed if all places are visited
        project.is_completed = True
    else:
        project.is_completed = False
    project.updated_at = datetime.now(timezone.utc)


# Project CRUD 

async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    places_data = data.places or []

    if len(places_data) < 1:
        raise BusinessError("A project must have at least 1 place")

    if len(places_data) > MAX_PLACES_PER_PROJECT:
        raise BusinessError(f"A project can have at most {MAX_PLACES_PER_PROJECT} places")

    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    db.add(project)
    await db.flush()  # get project.id before adding places

    for place_data in places_data:
        name = await _fetch_and_validate_place(place_data.external_id)
        place = Place(
            project_id=project.id,
            external_id=place_data.external_id,
            name=name,
        )
        db.add(place)

    await db.commit()
    await db.refresh(project)

    # reload with places
    return await _get_project_with_places(db, project.id)


async def list_projects(db: AsyncSession) -> List[Project]:
    result = await db.execute(
        select(Project).options(selectinload(Project.places)).order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: str) -> Project:
    return await _get_project_with_places(db, project_id)


async def update_project(db: AsyncSession, project_id: str, data: ProjectUpdate) -> Project:
    project = await _get_project_with_places(db, project_id)

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.start_date is not None:
        project.start_date = data.start_date

    project.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return await _get_project_with_places(db, project_id)


async def delete_project(db: AsyncSession, project_id: str) -> None:
    project = await _get_project_with_places(db, project_id)

    if any(p.is_visited for p in project.places):
        raise BusinessError("Cannot delete project with visited places")

    await db.delete(project)
    await db.commit()


# Place CRUD 

async def add_place(db: AsyncSession, project_id: str, data: PlaceCreate) -> Place:
    project = await _get_project_with_places(db, project_id)

    if len(project.places) >= MAX_PLACES_PER_PROJECT:
        raise BusinessError(f"Project already has {MAX_PLACES_PER_PROJECT} places")

    existing_ids = [p.external_id for p in project.places] # check duplicate
    if data.external_id in existing_ids:
        raise BusinessError(f"Place {data.external_id} already exists in this project")

    name = await _fetch_and_validate_place(data.external_id)

    place = Place(
        project_id=project_id,
        external_id=data.external_id,
        name=name,
    )
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return place


async def list_places(db: AsyncSession, project_id: str) -> List[Place]:
    await _get_project_with_places(db, project_id)  # validate project exists
    result = await db.execute(
        select(Place)
        .where(Place.project_id == project_id)
        .order_by(Place.created_at.asc())
    )
    return list(result.scalars().all())


async def get_place(db: AsyncSession, project_id: str, place_id: str) -> Place:
    await _get_project_with_places(db, project_id)
    result = await db.execute(
        select(Place).where(Place.id == place_id, Place.project_id == project_id)
    )
    place = result.scalar_one_or_none()
    if not place:
        raise PlaceNotFound(f"Place {place_id} not found in project {project_id}")
    return place


async def update_place(
    db: AsyncSession, project_id: str, place_id: str, data: PlaceUpdate
) -> Place:
    project = await _get_project_with_places(db, project_id)
    result = await db.execute(
        select(Place).where(Place.id == place_id, Place.project_id == project_id)
    )
    place = result.scalar_one_or_none()
    if not place:
        raise PlaceNotFound(f"Place {place_id} not found")

    if data.notes is not None:
        place.notes = data.notes
    if data.is_visited is not None:
        place.is_visited = data.is_visited

    place.updated_at = datetime.now(timezone.utc)

    # reload places for completion check
    await db.flush()
    await db.refresh(project)
    result2 = await db.execute(select(Place).where(Place.project_id == project_id))
    project.places = list(result2.scalars().all())
    await _check_project_completion(db, project)

    await db.commit()
    await db.refresh(place)
    return place
