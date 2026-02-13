import re

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, field_validator

from . import db
from .badge import render_badge

router = APIRouter(prefix="/api")

NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_name(name: str) -> str:
    if not NAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="Counter name must contain only letters, digits, hyphens, and underscores.",
        )
    return name


class CreateCounter(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        if not NAME_RE.match(v):
            raise ValueError(
                "Counter name must contain only letters, digits, hyphens, and underscores."
            )
        return v


@router.get("/counters")
async def list_counters():
    return await db.list_counters()


@router.post("/counters", status_code=201)
async def create_counter(body: CreateCounter):
    existing = await db.get_counter(body.name)
    if existing:
        raise HTTPException(status_code=409, detail="Counter already exists.")
    counter = await db.create_counter(body.name)
    return counter


@router.get("/counters/{name}")
async def get_counter(name: str):
    _validate_name(name)
    counter = await db.get_counter(name)
    if counter is None:
        raise HTTPException(status_code=404, detail="Counter not found.")
    return counter


@router.post("/counters/{name}/hit")
async def hit_counter(name: str):
    _validate_name(name)
    counter = await db.increment_counter(name)
    return counter


@router.get("/counters/{name}/badge.svg")
async def badge(
    name: str,
    label: str = Query(default="visitors"),
    color: str = Query(default="#007ec6"),
):
    _validate_name(name)
    counter = await db.get_counter(name)
    count = counter["count"] if counter else 0
    svg = render_badge(label, count, color)
    return Response(content=svg, media_type="image/svg+xml", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
    })


@router.get("/health")
async def health():
    return {"status": "ok"}
