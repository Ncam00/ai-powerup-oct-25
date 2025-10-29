"""
TODO: Create a Pydantic model for job opportunity extraction

Instructions:
1. Import BaseModel and Field from pydantic
2. Import Optional and List from typing
3. Create a JobPosting class that inherits from BaseModel
4. Add fields for: title, company, location, job_type, summary, requirements, salary_range

See README.md for detailed step-by-step instructions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class JobPosting(BaseModel):
    """A simple job posting model for structured output extraction"""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_type: Optional[str] = Field(
        None,
        description="Employment type (full-time, part-time, contract, etc.)",
    )
    summary: str = Field(..., description="Brief summary of the job")
    requirements: List[str] = Field(
        default_factory=list, description="Key job requirements"
    )
    salary_range: Optional[str] = Field(
        None, description="Salary range if mentioned"
    )
