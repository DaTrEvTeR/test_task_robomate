from typing import Optional
from pydantic import BaseModel, Field


class Experience(BaseModel):
    """Model representing work experience details."""

    position: Optional[str] = Field("", description="Position held in the company")
    company: Optional[str] = Field("", description="Name of the company")
    description: Optional[str] = Field("", description="Description of the job role")
    period: Optional[float] = Field(
        float(0), description="Duration of employment in years"
    )
