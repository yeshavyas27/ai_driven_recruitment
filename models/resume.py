from typing import List

from pydantic import BaseModel


class Education(BaseModel):
    institution: str | None
    degree: str | None
    GPA: str | None
    graduation: str | None
    coursework: List[str] | None


class Timeline(BaseModel):
    start: str | None
    end: str | None


class Experience(BaseModel):
    role: str | None
    organization: str | None
    timeline: Timeline | None
    details: List[str] | None
    skills_related: List[str] | None


class Project(BaseModel):
    name: str | None
    skills_related: List[str] | None
    details: List[str] | None


class Resume(BaseModel):
    name: str 
    linkedin: str | None = None
    github: str | None = None
    education: List[Education] | None = None
    skills: List[str] 
    experience: List[Experience] | None = None
    accomplishments_and_projects: List[Project] | None = None
    total_years_of_experience: str | None

