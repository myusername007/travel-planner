from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Place schemas

class PlaceCreate(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None


class PlaceResponse(BaseModel):
    id: str
    project_id: str
    external_id: int
    name: str
    notes: Optional[str]
    is_visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}




# Project schemas

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: List[PlaceCreate] = Field(..., min_length=1)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    start_date: Optional[date]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    places: List[PlaceResponse] = []

    model_config = {"from_attributes": True}
