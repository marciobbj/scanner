from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def _uuid4():
    return str(uuid4())


class BaseScanModelData(BaseModel):
    missing_fields: Optional[List[str]] = []
    uuid: str = Field(default_factory=_uuid4)
