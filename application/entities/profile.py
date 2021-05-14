from typing import Dict, List
from pydantic import BaseModel, root_validator
import datetime


class Address(BaseModel):
    line1: str
    line2: str
    city: str
    state: str
    postal_code: str
    country: str

class Profile(BaseModel):
    id: str
    account: str
    username: str
    employer: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone_number: str
    birth_date: datetime.date
    picture_url: str 
    address: Address
    ssn: str
    marital_status: str
    gender: str
    metadata: dict
    employment_status: str
    employment_type: str
    job_title: str
    platform_user_id: str
    hire_dates: List[datetime.datetime]
    terminations: List[Dict[str, str]]
