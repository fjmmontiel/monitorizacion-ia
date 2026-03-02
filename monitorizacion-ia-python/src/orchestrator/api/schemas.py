from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator



SUPPORTED_COMPONENT_TYPES = {'cards', 'table', 'detail', 'chart', 'text'}
MAX_COMPONENTS_PER_VIEW = 20
MAX_COMPONENTS_PER_TYPE = 8
MAX_CONFIG_ENTRIES = 40
COMPONENT_DATA_SOURCES = {
    'cards': {'/cards'},
    'table': {'/dashboard'},
    'detail': {'/dashboard_detail', '/none'},
    'chart': {'/dashboard', '/cards', '/none'},
    'text': {'/none'},
}

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


class ViewComponent(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: str = Field(min_length=1, max_length=80)
    type: Literal['cards', 'table', 'detail', 'chart', 'text']
    title: str = Field(min_length=1, max_length=120)
    data_source: str = Field(min_length=1, max_length=120)
    position: int = Field(default=0, ge=0, le=200)
    config: dict[str, Any] | None = None

    @model_validator(mode='after')
    def validate_component(self):
        allowed_sources = COMPONENT_DATA_SOURCES.get(self.type, set())
        if self.data_source not in allowed_sources:
            raise ValueError(f'invalid data_source {self.data_source} for component type {self.type}')
        if self.config is not None and len(self.config) > MAX_CONFIG_ENTRIES:
            raise ValueError(f'config too large for component {self.id}; max entries: {MAX_CONFIG_ENTRIES}')
        return self


class ViewConfiguration(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    system: str = Field(min_length=1, max_length=80)
    enabled: bool = True
    components: list[ViewComponent]

    @model_validator(mode='after')
    def validate_components_semantics(self):
        if len(self.components) == 0:
            raise ValueError('components cannot be empty')
        if len(self.components) > MAX_COMPONENTS_PER_VIEW:
            raise ValueError(f'too many components; max: {MAX_COMPONENTS_PER_VIEW}')

        ids = [component.id for component in self.components]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicated component ids are not allowed')

        supported_types = {component.type for component in self.components}
        unsupported = supported_types.difference(SUPPORTED_COMPONENT_TYPES)
        if unsupported:
            raise ValueError(f'unsupported component types: {sorted(unsupported)}')

        type_counts: dict[str, int] = {}
        for component in self.components:
            type_counts[component.type] = type_counts.get(component.type, 0) + 1
        overflowing = [component_type for component_type, count in type_counts.items() if count > MAX_COMPONENTS_PER_TYPE]
        if overflowing:
            raise ValueError(f'too many components by type: {overflowing}; max per type {MAX_COMPONENTS_PER_TYPE}')

        return self


class ViewConfigCreate(ViewConfiguration):
    pass


class ViewConfigUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str | None = Field(default=None, min_length=1, max_length=150)
    system: str | None = Field(default=None, min_length=1, max_length=80)
    enabled: bool | None = None
    components: list[ViewComponent] | None = None
