# Travel Planner API

A REST API for managing travel projects and places. Places are validated against the [Art Institute of Chicago API](https://api.artic.edu/docs/).

## Tech Stack

- Python 3.12, FastAPI
- SQLite + SQLAlchemy 2.x (async)
- Docker Compose

## Getting Started

### Run locally

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

### Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

API will be available at `http://localhost:8010`

Swagger docs: `http://localhost:8010/docs`

## API Overview

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects` | Create a project |
| GET | `/api/v1/projects` | List all projects |
| GET | `/api/v1/projects/{id}` | Get a single project |
| PATCH | `/api/v1/projects/{id}` | Update project info |
| DELETE | `/api/v1/projects/{id}` | Delete project (blocked if any place is visited) |

### Places

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects/{id}/places` | Add a place to a project |
| GET | `/api/v1/projects/{id}/places` | List all places in a project |
| GET | `/api/v1/projects/{id}/places/{place_id}` | Get a single place |
| PATCH | `/api/v1/projects/{id}/places/{place_id}` | Update notes or mark as visited |

## Business Rules

- A project can have 1–10 places
- The same place cannot be added to the same project twice
- A project cannot be deleted if any of its places are marked as visited
- When all places in a project are visited, the project is automatically marked as completed
- Places are validated against the Art Institute of Chicago API before being stored

## Example Requests

**Create a project with places:**
```json
POST /api/v1/projects
{
  "name": "Chicago Art Trip",
  "description": "Places I want to visit",
  "start_date": "2026-06-01",
  "places": [
    {"external_id": 27992},
    {"external_id": 28560}
  ]
}
```

**Add a place to existing project:**
```json
POST /api/v1/projects/{project_id}/places
{
  "external_id": 27992
}
```

**Mark a place as visited:**
```json
PATCH /api/v1/projects/{project_id}/places/{place_id}
{
  "is_visited": true
}
```

**Update notes:**
```json
PATCH /api/v1/projects/{project_id}/places/{place_id}
{
  "notes": "Sculpture gallery"
}
```

## Finding Place IDs

Use the Art Institute of Chicago API to search for artworks:
```
GET https://api.artic.edu/api/v1/artworks/search?q=monet&limit=5
```

The `id` field in the response is the `external_id` to use.
