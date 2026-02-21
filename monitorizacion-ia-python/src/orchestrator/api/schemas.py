from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueryModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    filters: list[dict[str, Any]] = Field(default_factory=list)
    search: str | None = None
    sort: list[dict[str, Any]] = Field(default_factory=list)
    cursor: str | None = None
    limit: int | None = None


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    query: QueryModel = Field(default_factory=QueryModel)


class CardItem(BaseModel):
    id: str
    title: str
    value: str | int | float


class CardsResponse(BaseModel):
    schema_version: str = 'v1'
    cards: list[CardItem]


class DashboardActionPayload(BaseModel):
    id: str


class DashboardAction(BaseModel):
    type: str = 'dashboard_detail'
    payload: DashboardActionPayload


class DashboardRow(BaseModel):
    id: str
    data: dict[str, Any]
    detail: DashboardAction


class DashboardResponse(BaseModel):
    schema_version: str = 'v1'
    columns: list[str]
    rows: list[DashboardRow]
    next_cursor: str | None = None


class DashboardDetailRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: str
    query: QueryModel | None = None


class MessageBlock(BaseModel):
    role: str
    text: str


class DetailBlock(BaseModel):
    type: str
    title: str
    content: dict[str, Any]


class DashboardDetailResponse(BaseModel):
    schema_version: str = 'v1'
    id: str
    left: dict[str, list[MessageBlock]]
    right: dict[str, list[DetailBlock]]
