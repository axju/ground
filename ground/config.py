from pathlib import Path
from pydantic import BaseModel, Field, field_serializer, field_validator
from platformdirs import user_config_dir

import toml


DEFAULT_CONFIG_PATH: Path = Path(user_config_dir("ground")) / "config.toml"


class Config(BaseModel):

    # A list with project paths
    project_root: Path | None = None

    # html export path
    html_export_dir: Path | None = None

    # Convert Path to string when serializing
    @field_serializer("project_root", "html_export_dir")
    def serialize_path(self, path: Path | None) -> str | None:
        return str(path) if path is not None else None
    
    # Convert string back to Path when deserializing
    @field_validator("project_root", "html_export_dir", mode='before')
    @classmethod
    def validate_path(cls, value: any) -> Path | None:
        if value is None:
            return None
        return Path(value)

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH):
        with path.open("r") as f:
            data = toml.load(f)
        return cls.model_validate(data)

    def save(self, path: Path = DEFAULT_CONFIG_PATH):
        with path.open("w") as f:
            toml.dump(self.model_dump(), f)


if __name__ == "__main__":
    config: Config = Config.load()
    print(config.model_dump_json(indent=4))
