from application.entities.upwork.page_scans import MainPageData
from application.validators import clean_scan_data
import pytest
from unittest import mock

@pytest.mark.parametrize("data,schema,expected_output", [
    (
        {
            "username": "username",
            "profile_visibility": "20",
            "available_hours": "20 Hours",
            "profile_completion": "80%",
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        },
        MainPageData,
        {
            "uuid": mock.ANY, # auto generated uuid
            "username": "username",
            "profile_visibility": "20",
            "missing_fields": [],
            "available_hours": "20 Hours",
            "profile_completion": "80%",
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        }
    )
])
def test_clean_scan_data_happy_path(data, schema, expected_output):
    cleaned_data = clean_scan_data(schema, data)
    assert cleaned_data == expected_output


@pytest.mark.parametrize("data,schema,expected_output", [
    (
        {
            "profile_visibility": "20",
            "available_hours": "20 Hours",
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        },
        MainPageData,
        {
            "username": None,
            "profile_visibility": "20",
            "missing_fields": ['username', 'profile_completion'],
            "available_hours": "20 Hours",
            "profile_completion": None,
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        }
    ),
    (
        {
            "profile_visibility": "20",
            "available_hours": "20 Hours",
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        },
        MainPageData,
        {
            "username": None,
            "profile_visibility": "20",
            "missing_fields": ['username', 'profile_completion'],
            "available_hours": "20 Hours",
            "profile_completion": None,
            "proposals": "70 proposals",
            "categories": ["IT", "DBA"]
        }
    ),
    (
        {
            "profile_visibility": "20",
            "available_hours": "20 Hours",
        },
        MainPageData,
        {
            "username": None,
            "profile_visibility": "20",
            "missing_fields": ['username', 'profile_completion', 'proposals', 'categories'],
            "available_hours": "20 Hours",
            "profile_completion": None,
            "proposals": None,
            "categories": None
        }
    )
])
def test_clean_scan_data_with_missing_fields(data, schema, expected_output):
    cleaned_data = clean_scan_data(schema, data)
    assert cleaned_data == expected_output
