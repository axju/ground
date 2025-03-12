from pathlib import Path
from pydantic import BaseModel, Field


class Resource(BaseModel):
    identifier: int
    name: str
    price: float


class ProjectMeta(BaseModel):
    desc: str = "default"
    spec: str = "default"
    parts: str = "default"
    media: Path = Path("media")


class ProjectDescription(BaseModel):
    name: str = ""
    description: str = ""
    identifier: int = 0


class ProjectSpecifications(BaseModel):
    ...


class ProjectMedia(BaseModel):
    images: list[Path] = Field(default_factory=list)
    videos: list[Path] = Field(default_factory=list)


class ProjectPartItem(BaseModel):
    count: int = 1
    resource: Resource


class ProjectCalculation(BaseModel):
    price: float = 0


class Project(BaseModel):
    path: Path
    meta: ProjectMeta = Field(default_factory=ProjectMeta)
    desc: ProjectDescription = Field(default_factory=ProjectDescription)
    spec: ProjectSpecifications = Field(default_factory=ProjectSpecifications)
    parts: list[ProjectPartItem] = Field(default_factory=list)
    calc: ProjectCalculation = Field(default_factory=ProjectCalculation)


class Product(BaseModel):
    identifier: int
    name: str
    description: str = ""
    price: float = 0
    images: list[str] = Field(default_factory=list)