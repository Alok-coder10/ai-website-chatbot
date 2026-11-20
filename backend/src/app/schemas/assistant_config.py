from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssistantConfigCreate(BaseModel):
    """Fields required to create an assistant configuration."""

    name: str = Field(default="My Assistant", min_length=1, max_length=150)
    system_prompt: str = Field(
        default="You are a helpful website assistant. Answer clearly and accurately.",
        min_length=1,
    )
    llm_provider: str = Field(default="ollama", min_length=1, max_length=50)
    llm_model: str = Field(default="llama3.2:3b", min_length=1, max_length=150)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=128000)
    welcome_message: str = Field(
        default="Hi! How can I help you today?",
        max_length=500,
    )
    primary_color: str = Field(default="#2563EB", pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool = True


class AssistantConfigUpdate(BaseModel):
    """Fields that can be changed on an existing assistant configuration."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    system_prompt: str | None = Field(default=None, min_length=1)
    llm_provider: str | None = Field(default=None, min_length=1, max_length=50)
    llm_model: str | None = Field(default=None, min_length=1, max_length=150)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    welcome_message: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    is_active: bool | None = None


class AssistantConfigResponse(BaseModel):
    """Public API representation of an assistant configuration."""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    system_prompt: str
    llm_provider: str
    llm_model: str
    temperature: float
    max_tokens: int
    welcome_message: str
    primary_color: str
    is_active: bool
