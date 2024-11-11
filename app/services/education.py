from typing import Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """Model representing education details."""

    name: Optional[str] = Field("", description="Name of the educational institution")
    comment: Optional[str] = Field("", description="Additional comments or details")
    location: Optional[str] = Field(
        "", description="The location where the education was received"
    )
    speciality: Optional[str] = Field(
        "", description="Specialization or field of study"
    )
    year_of_graduation: Optional[int] = Field(0, description="Year of graduation")
