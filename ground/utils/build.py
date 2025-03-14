from __future__ import annotations
from pathlib import Path
import json
import shutil

from jinja2 import Environment, FileSystemLoader

from ground.config import Config
from ground.model import Project, Product
from ground.utils import ProjectIterMode, projects_all, project_media_iter, project_to_product


def products_save_json(products: list[Product], path: Path):
    """
    save product list into a json file 
    """
    data = [product.model_dump() for product in products]
    with path.open("w") as f:
        json.dump(data, f, indent=4)


def generate_html(product: Product, path: Path, template_env: Environment):
    """
    parth ist th html project directory
    """
    data = product.model_dump()
    template = template_env.get_template('product.html')
    rendered_html = template.render(data)

    with Path(path / f"{product.identifier}.html").open("w") as f:
        f.write(rendered_html)


def render_template(name: str, path: Path, template_env: Environment, **kwargs):
    template = template_env.get_template(name)
    rendered_html = template.render(kwargs)

    with path.open("w") as f:
        f.write(rendered_html)


def setup_html(template_path: Path = Path(__file__).parent.parent / "templates") -> Environment:
    template_loader = FileSystemLoader(str(template_path))
    return Environment(loader=template_loader)


def make_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_html(config: Config):
    template_env = setup_html()
    build_projects_path: Path = make_dir(config.html / "products")

    for name in ["index", "products"]:
        render_template(f"{name}.html", config.html / f"{name}.html", template_env)

    products = []
    for project in projects_all(config):
        print(project)
        product = project_to_product(project)
        build_product_media: Path = make_dir(config.html / f"media/product/{product.identifier}")

        generate_html(product, build_projects_path, template_env)
        for image in project_media_iter(project):
            shutil.copy(image, build_product_media / f"{image.name}")

        products.append(product)

    products_save_json(products, config.html / "products.json")


def cli():
    config = Config.load()
    build_html(config)


if __name__ == "__main__":
    cli()