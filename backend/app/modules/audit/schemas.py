from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditEventRead(BaseModel):
    id: str
    actor_user_id: str | None
    actor_username: str
    actor_name: str
    module: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    before_data: dict | None
    after_data: dict | None
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditEventCreate(BaseModel):
    module: str = Field(max_length=80)
    action: str = Field(max_length=80)
    entity_type: str = Field(max_length=80)
    entity_id: str = Field(default="", max_length=80)
    summary: str = Field(default="", max_length=260)
    before_data: dict | None = None
    after_data: dict | None = None
    reason: str = ""
