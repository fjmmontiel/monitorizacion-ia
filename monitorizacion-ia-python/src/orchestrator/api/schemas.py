from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SortItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    field: str
    direction: Literal['asc', 'desc']


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    timeRange: str | None = None
    filters: dict[str, Any] | None = None
    search: str | None = None
    sort: list[SortItem] | None = None
    cursor: str | None = None
    limit: int | None = Field(default=None, ge=1)


class CardItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str
    subtitle: str | None = None
    value: str | int | float
    format: Literal['seconds', 'percent', 'currencyEUR', 'int', 'float'] | None = None


class CardsResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    cards: list[CardItem]


class TableColumn(BaseModel):
    model_config = ConfigDict(extra='forbid')

    key: str
    label: str
    filterable: bool | None = None
    sortable: bool | None = None


class DetailAction(BaseModel):
    model_config = ConfigDict(extra='forbid')

    action: str = 'Ver detalle'


class TableRow(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: str
    detail: DetailAction


class TablePayload(BaseModel):
    model_config = ConfigDict(extra='forbid')

    columns: list[TableColumn]
    rows: list[TableRow]
    nextCursor: str | None = None


class DashboardResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    table: TablePayload


class MessageBlock(BaseModel):
    model_config = ConfigDict(extra='forbid')

    role: str
    text: str
    timestamp: str | None = None


class LeftPanel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    messages: list[MessageBlock]


class KVItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    key: str
    value: str


class KVPanel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type: Literal['kv']
    title: str
    items: list[KVItem]


class ListPanel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type: Literal['list']
    title: str
    items: list[str]


class TimelineEvent(BaseModel):
    model_config = ConfigDict(extra='forbid')

    label: str
    time: str | None = None


class TimelinePanel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type: Literal['timeline']
    title: str
    events: list[TimelineEvent]


class MetricItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    label: str
    value: str | int | float


class MetricsPanel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type: Literal['metrics']
    title: str
    metrics: list[MetricItem]


RightPanel = Annotated[KVPanel | ListPanel | TimelinePanel | MetricsPanel, Field(discriminator='type')]


class DashboardDetailResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    left: LeftPanel
    right: list[RightPanel]


class DatopsRoutes(BaseModel):
    model_config = ConfigDict(extra='forbid')

    cards: str
    dashboard: str
    dashboard_detail: str


class DatopsUseCase(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: str
    adapter: str
    timeout_ms: int
    upstream_base_url: str | None = None
    routes: DatopsRoutes


class DatopsOverviewResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    schema_version: str = 'v1'
    generated_at: str
    profile: str
    use_cases: list[DatopsUseCase]
