from pathlib import Path

from ground.config import Config
from ground.model import Project

from ground.utils import projects_all
from ground.utils.build import build_html


class GroundProject:

    def __init__(self, project: Project):
        super().__init__()
        self.data = project
        self.images: list[Path] = []

        self.update()

    def update(self):
        self.images = ["123123", "asdasd"]

class Ground:

    def __init__(self, config: Config = Config.load()):
        self.config: Config = config
        self.projects: list[GroundProject] = []

    def update(self):
        self.projects = [GroundProject(project) for project in projects_all(self.config)]

    def build_html(self):
        """
        export all products to an html page
        """
        build_html(self.config)
