from pydantic.fields import Field
from application.entities import BaseScanModelData
from application.entities.upwork.profile import (
    Address,
    Certificate,
    Contact,
    Education,
    Experience,
    Language,
)
from typing import List, Optional


class ProfilePageData(BaseScanModelData):
    """Represents partial scan from profile page."""

    full_name: Optional[str] = Field(...)
    city: Optional[str] = Field(...)
    country: Optional[str] = Field(...)
    price_per_hour: Optional[str] = Field(...)
    profile_description: Optional[str] = Field(...)
    professional_experiences: Optional[List[Experience]] = Field(...)
    languages: Optional[List[Language]] = Field(...)
    education: List[Education] = Field(...)
    certificates: List[Certificate] = Field(...)
    picture_url: Optional[str] = Field(...)
    job_title: Optional[str] = Field(...)


class ContactInfoData(BaseScanModelData):
    """Represents partial scan from contact info page."""

    email: Optional[str] = Field(...)
    timezone: Optional[str] = Field(...)
    street: Optional[str] = Field(...)
    street_complement: Optional[str] = Field(...)
    zipcode: Optional[str] = Field(...)
    phone_number: Optional[str] = Field(...)
    country_code: Optional[str] = Field(...)


class MainPageData(BaseScanModelData):
    """Represents partial scan from upwork main page platform."""

    username: Optional[str] = Field(...)
    profile_visibility: Optional[str] = Field(...)
    available_hours: Optional[str] = Field(...)
    profile_completion: Optional[str] = Field(...)
    proposals: Optional[str] = Field(...)
    categories: Optional[List[str]] = Field(...)


class FullScanProfile(BaseScanModelData):
    """Represents full scan from upwork platform."""

    uuid: Optional[str] = Field(...)

    full_name: Optional[str] = Field(...)

    address: Optional[Address] = Field(...)

    contact: Optional[Contact] = Field(...)

    country_code: Optional[str] = Field(...)

    profile_description: Optional[str] = Field(...)

    professional_experiences: Optional[List[Experience]] = Field(...)

    languages: Optional[List[Language]] = Field(...)

    education: Optional[List[Education]] = Field(...)

    certificates: Optional[List[Certificate]] = Field(...)

    created_at: Optional[str] = Field(...)

    updated_at: Optional[str]
    picture_url: Optional[str] = Field(...)

    job_title: Optional[str] = Field(...)
