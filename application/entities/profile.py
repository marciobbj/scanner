from application.entities import BaseScanModelData
from typing import Dict, List, Optional
import datetime


class Language(BaseScanModelData):
    language: str
    profiency: str


class Education(BaseScanModelData):
    title: str
    field: str
    period: str


class Experiences(BaseScanModelData):
    role: str
    period: str
    comment: str


class Certificate(BaseScanModelData):
    title: str
    description: str


class Address(BaseScanModelData):
    city: str
    country: str


class ProfilePageData(BaseScanModelData):
    uuid: str = ...
    full_name: str = ...
    address: Address = ...
    price_per_hour: str = ...
    profile_description: str = ...
    professional_experiences: List[Experiences] = ...
    languages: List[Language] = ...
    education: List[Education] = ...
    certificates: List[Certificate] = ...
    created_at: datetime.datetime = ...
    updated_at: Optional[datetime.datetime]
    picture_url: str = ...
    job_title: str = ...