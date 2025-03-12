from pathlib import Path
from pydantic import BaseModel, Field

import toml


DEFAULT_CONFIG_PATH: Path = Path("config.toml")
DEFAULT_HTML_PATH: Path = Path("build/html")


class Config(BaseModel):

    # A list with project paths
    projects: list[Path] = Field(default_factory=list)

    # html export path
    html: Path = Field(default=DEFAULT_HTML_PATH)


    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH):
        with path.open("r") as f:
            data = toml.load(f)
        return cls.model_validate(data)

