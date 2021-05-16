from application.entities import BaseScanModelData
from typing import Optional
from pydantic import Field


class Language(BaseScanModelData):
    language: Optional[str] = Field(...)
    profiency: Optional[str] = Field(...)


class Education(BaseScanModelData):
    title: Optional[str] = Field(...)
    field: Optional[str] = Field(...)
    period: Optional[str] = Field(...)


class Experience(BaseScanModelData):
    role: Optional[str] = Field(...)
    period: Optional[str] = Field(...)
    comment: Optional[str]


class Certificate(BaseScanModelData):
    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)


class Address(BaseScanModelData):
    city: Optional[str] = Field(...)
    country: Optional[str] = Field(...)
    street: Optional[str] = Field(...)
    street_complement: Optional[str] = Field(...)
    zipcode: Optional[str] = Field(...)
    timezone: Optional[str] = Field(...)


class Contact(BaseScanModelData):
    phone_number: Optional[str] = Field(...)
    email: Optional[str] = Field(...)
