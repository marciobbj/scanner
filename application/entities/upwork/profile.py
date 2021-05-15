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
    comment: Optional[str]


class Certificate(BaseScanModelData):
    title: str
    description: str


class Address(BaseScanModelData):
    city: str = ...
    country: str = ...
    street: str = ...
    street_complement: str = ...
    zipcode: str = ...
    timezone: str = ...


class Contact(BaseScanModelData):
    phone_number: str = ...
    email: str = ...
