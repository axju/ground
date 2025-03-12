from pathlib import Path
from enum import Enum
import json

import toml

from .config import Config
from .model import Project, ProjectDescription, Product


class ProjectIterMode(Enum):
    AI = "ai"
    DIR = "dir"
    JSON = "json"


def projects_save_json(projects: list[Project], path: Path):
    for project in projects:
        print(project)


def projects_iter(mode: ProjectIterMode = ProjectIterMode.DIR, **kwargs: any):
    match mode:
        case ProjectIterMode.AI:
            n = kwargs.get("n", 5)
            for i in range(n):
                yield Project.generate(i, ai=kwargs.get("ai", True))

        case ProjectIterMode.DIR:
            path = Path(kwargs.get("path"))
            for item in path.iterdir():
                if item.is_dir():
                    yield project_load(item.resolve())

        case ProjectIterMode.JSON:
            path = Path(kwargs.get("path"))
            projects = []
            with path.open("r") as f:
                projects = json.load(f)
            for project in projects:
                yield Project.loaddict(project)


def projects_all(config: Config):
    for project_dir in config.projects:
        yield from projects_iter(mode=ProjectIterMode.DIR, path=project_dir)


def project_media_iter(project: Project):
    path: Path = Path(project.path / "media")
    if not path.is_dir():
        return
    for path in path.iterdir():
        yield path


def project_load(path: Path) -> Project:
        meta_path: Path = Path(path / "ground.toml")
        project = Project(path=path)
        if meta_path.is_file():
            with meta_path.open("r") as f:
                data = toml.load(f)
            data['path'] = path
            project = Project.model_validate(data)
            #project.meta.path = meta_path

        project_update_desc(project)
        return project


def project_to_product(project: Project) -> Product | None:
    return Product(
        identifier=project.desc.identifier,
        name=project.desc.name,
        description=project.desc.description,
        price=project.calc.price,
        images=[path.name for path in project_media_iter(project)]
    )


def project_update_desc(project: Project):
    match project.meta.desc:
        case "skipp":
            ...
        case _:
            for name in ["info.txt", "ground.txt"]:
                desc_update(project.desc, project.path / name)


def desc_update(desc: ProjectDescription, path: Path) -> ProjectDescription | None:
    if not path.is_file():
        return
    
    with path.open("r") as f:
        lines = f.readlines()
    desc.name = lines[0]

    for line in lines[1:]:
        if len(line) < 2:
            continue
        if line.startswith('id:'):
            desc.identifier = line.split(":")[1].strip()
            continue
        desc.description += line.strip()
    return desc
            
