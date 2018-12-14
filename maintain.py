"""OS agnostic script for running code maintainance tasks"""
import os
from subprocess import run
import click


@click.command()
@click.option("--black", default=True, help="Use black (linting)?")
@click.option("--pylint", default=True, help="Use pylint (linting)?")
@click.option("--mypy", default=True, help="Use mypy (typing)?")
@click.option("--pytest", default=True, help="Use pytest (testing)?")
def maintain(black, pylint, mypy, pytest):
    """Run various maintainance tools for linting, testing and anything else"""
    if black:
        click.echo("")
        click.echo("****************** Running black ****************** ")
        click.echo("")
        result = run(["black", "."]).returncode
        if result != 0:
            return result
    if pylint:
        click.echo("")
        click.echo("****************** Running pylint ****************** ")
        click.echo("")
        with open("__init__.py", "w") as open_file:
            open_file.write("")
        result = run(["pylint", "app"]).returncode
        os.remove("__init__.py")
        if result != 0:
            return result
    if mypy:
        click.echo("")
        click.echo("****************** Running mypy ****************** ")
        click.echo("")
        result = run(["mypy", "."]).returncode
        if result != 0:
            return result
    if pytest:
        click.echo("")
        click.echo("****************** Running pytest ****************** ")
        click.echo("")
        result = run(["pytest"]).returncode
        if result != 0:
            return result


if __name__ == "__main__":
    maintain()
