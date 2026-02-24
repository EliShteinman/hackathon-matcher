from pydantic import BaseModel, ConfigDict, Field


class ExcelRowSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_number: str = Field(..., min_length=1)
    email: str = Field(...)
    full_name: str = Field(..., min_length=1)
    branch: str = Field(...)
    phone: str | None = Field(default=None)
