"""A collection of CLI commands for working with registered Kedro pipelines."""
from pathlib import Path

import click
import yaml

from kedro.framework.cli.utils import KedroCliError, command_with_verbosity
from kedro.framework.project import pipelines
from kedro.framework.startup import ProjectMetadata


# noqa: missing-function-docstring
@click.group(name="Kedro")
def registry_cli():  # pragma: no cover
    pass


@registry_cli.group()
def registry():
    """Commands for working with registered pipelines."""


@registry.command("list")
def list_registered_pipelines():
    """List all pipelines defined in your pipeline_registry.py file."""
    click.echo(yaml.dump(sorted(pipelines)))


@command_with_verbosity(registry, "describe")
@click.argument("name", nargs=1, default="__default__")
@click.pass_obj
def describe_registered_pipeline(
    metadata: ProjectMetadata, name, **kwargs
):  # noqa: unused-argument, protected-access
    """Describe a registered pipeline by providing a pipeline name.
    Defaults to the `__default__` pipeline.
    """
    pipeline_obj = pipelines.get(name)
    if not pipeline_obj:
        all_pipeline_names = pipelines.keys()
        existing_pipelines = ", ".join(sorted(all_pipeline_names))
        raise KedroCliError(
            f"'{name}' pipeline not found. Existing pipelines: [{existing_pipelines}]"
        )

    nodes = []
    for node in pipeline_obj.nodes:
        namespace = f"{node.namespace}." if node.namespace else ""
        nodes.append(f"{namespace}{node._name or node._func_name} ({node._func_name})")
    result = {"Nodes": nodes}

    click.echo(yaml.dump(result))


@command_with_verbosity(registry, "export")
@click.argument("name", nargs=1, default="__default__")
@click.option(
    "-o",
    "--output-file",
    help="File path to export the pipeline to. Suffix must be .json",
    type=click.Path(dir_okay=False, writable=True, path_type=Path, resolve_path=True),
)
@click.pass_obj
def export_registered_pipeline(
    metadata: ProjectMetadata, name: str, output_file: Path, **kwargs
) -> None:  # noqa: unused-argument, protected-access
    """Export a registered pipeline by providing a pipeline name."""
    if output_file.suffix != ".json":
        raise KedroCliError(
            f"Output file must be a .json file. Received: '{output_file}'"
        )

    pipeline_obj = pipelines.get(name)
    if not pipeline_obj:
        all_pipeline_names = pipelines.keys()
        existing_pipelines = ", ".join(sorted(all_pipeline_names))
        raise KedroCliError(
            f"'{name}' pipeline not found. Existing pipelines: [{existing_pipelines}]"
        )

    output_file.write_text(pipeline_obj.dumps())
    click.echo(f"Pipeline '{name}' was exported successfully to '{output_file}'.")
