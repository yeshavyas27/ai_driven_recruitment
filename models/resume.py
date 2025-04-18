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
    name: str | None
    linkedin: str | None
    github: str | None
    education: List[Education] | None
    skills: List[str] | None
    experience: List[Experience] | None
    accomplishments_and_projects: List[Project] | None 
    total_years_of_experience: str | None

