import logging
from pydantic.error_wrappers import ValidationError
from pydantic.main import BaseModel


logger = logging.getLogger(__name__)


def clean_scan_data(schema_cls: BaseModel, data: dict):
    """Clean :data: and validates it.

    First it removes all fields that are None from :data: 
    and then if ValidationError is raised, the function 
    will fill these fields with "None", and append field's 
    identifier to the "missing_fields" list of the return dict.
    """
    filtered_data = {k: v for k, v in data.items() if v not in [[], None]}
    try:
        cleaned_data = schema_cls(**filtered_data)
        return cleaned_data.dict()
    except ValidationError as e:
        errors = e.errors()
        fields_missing = []
        logger.error("Scanner is not finding some required fields, validation error %s", repr(errors))  # noqa
        for error in errors:
            field = error["loc"][0]
            if error["type"] == "value_error.missing":
                logger.warning("Scanner is filling missing (%s) field with \"None\"", field)  # noqa
                data[field] = None
                fields_missing.append(field)
        data["missing_fields"] = fields_missing
        return schema_cls(**data).dict()
