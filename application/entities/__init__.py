from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel


class BaseScanModelData(BaseModel):
    missing_fields: Optional[List[str]] = []
    uuid: str = str(uuid4())


