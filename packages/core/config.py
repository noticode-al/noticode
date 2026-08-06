from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class AppConfig(BaseModel):
    """Noticode uygulama ayarlarını temsil eder."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    app_name: str = Field(default="Noticode", min_length=2, max_length=100)
    environment: str = Field(default="development", min_length=2, max_length=50)
    debug: bool = False
    workspace_root: Path = Field(default=Path.cwd())
    data_directory: Path = Field(default=Path("data"))
    log_level: str = Field(default="INFO", min_length=4, max_length=20)
