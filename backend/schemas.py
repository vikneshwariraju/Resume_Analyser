"""Step 3: the resume schema. Every field is Optional: a missing value must be None (null), never invented."""
from typing import Optional
from pydantic import BaseModel, field_validator

NULL_WORDS = {"", "null", "none", "n/a", "na", "not provided", "not specified", "not available", "-"}


def clean_value(v):
    """Turn blank / placeholder strings into None; trim real strings."""
    if isinstance(v, str):
        v = v.strip()
        return None if v.lower() in NULL_WORDS else v
    return v


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    score: Optional[str] = None      # CGPA / percentage, kept as text

    @field_validator("*", mode="before")
    @classmethod
    def _clean(cls, v):
        return clean_value(v)


class Experience(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

    @field_validator("*", mode="before")
    @classmethod
    def _clean(cls, v):
        return clean_value(v)


class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[list[str]] = None

    @field_validator("*", mode="before")
    @classmethod
    def _clean(cls, v):
        return clean_value(v)


class Resume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[list[str]] = None
    education: Optional[list[Education]] = None
    experience: Optional[list[Experience]] = None
    projects: Optional[list[Project]] = None          # detailed level only
    certifications: Optional[list[str]] = None        # detailed level only
    links: Optional[list[str]] = None                 # detailed level only

    @field_validator("name", "email", "phone", mode="before")
    @classmethod
    def _clean(cls, v):
        return clean_value(v)