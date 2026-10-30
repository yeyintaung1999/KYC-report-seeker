from pydantic import BaseModel, ConfigDict, Field


class DocumentBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class KYCSource(DocumentBaseModel):
    title: str = Field(
        ...,
        description="Original title of the adverse media article or official report.",
    )
    url: str = Field(
        ...,
        description="Original, full URL of the specific adverse source.",
    )
    description: str = Field(
        ...,
        description="Specific evidence-based finding summarizing the adverse content.",
    )
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Evidentiary strength score (0-100).",
    )


class KYCReportDetails(DocumentBaseModel):
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk severity score (0 to 100).",
    )
    summary: str = Field(
        ...,
        description="Concise investigation summary (max 3 sentences) synthesizing verified evidence.",
    )
    sources: list[KYCSource] = Field(
        default_factory=list,
        description="Array of distinct, evidence-based adverse sources.",
    )


class KYCReport(DocumentBaseModel):
    case_id: str = Field(..., description="Unique input tracking identifier.")
    name: str = Field(..., description="Exact full name of the individual subject.")
    company_name: str = Field(..., description="Exact official name of the company.")
    company_address: str | None = Field(
        default=None, description="Official registered address or null."
    )
    report: KYCReportDetails = Field(..., description="Compliance report details.")
    duration_ms: int = Field(..., ge=0, description="Total execution duration in ms.")
    agent_failed: bool = Field(default=False, description="Failure status boolean.")
    completed_at: str = Field(
        ..., description="ISO 8601 formatted completion timestamp."
    )