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


class ProfilePageData(BaseScanModelData):
    """Represents partial scan from profile page."""
    full_name: str = ...
    city: str = ...
    country: str = ...
    price_per_hour: str = ...
    profile_description: str = ...
    professional_experiences: List[Experiences] = ...
    languages: List[Language] = ...
    education: List[Education] = ...
    certificates: List[Certificate] = ...
    picture_url: str = ...
    job_title: str = ...


class ContactInfoData(BaseScanModelData):
    """Represents partial scan from contact info page."""
    email: str = ...
    timezone: str = ...
    street: str = ...
    street_complement: str = ...
    zipcode: str = ...
    phone_number: str = ...
    country_code: str = ...


class FullScanProfile(BaseScanModelData):
    """Represents full scan from upwork platform."""
    uuid: str = ...
    full_name: str = ...
    address: Address = ...
    contact: Contact = ...
    country_code: str = ...
    profile_description: str = ...
    professional_experiences: List[Experiences] = ...
    languages: List[Language] = ...
    education: List[Education] = ...
    certificates: List[Certificate] = ...
    created_at: str = ...
    updated_at: Optional[str]
    picture_url: str = ...
    job_title: str = ...
