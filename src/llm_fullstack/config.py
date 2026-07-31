from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

load_dotenv(Path(__file__).resolve().parents[3] / "FineTuning" / ".env")
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    rag_service_url: str
    model_service_url: str
    model_name: str
    model_api_key: str = Field(
        default="not-needed",
        validation_alias=AliasChoices("MODEL_API_KEY", "OPEN_ROUTER_API_KEY"),
    )

    mcp_server_command: str
    mcp_server_args: Annotated[list[str], NoDecode]

    agent_step_cap: int = 8

    @field_validator("mcp_server_args", mode="before")
    @classmethod
    def _split_csv(cls, v: str | list[str]) -> list[str]:
        return v.split(",") if isinstance(v, str) else v


settings = Settings()
