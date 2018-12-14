"""OS agnostic script for running code maintainance tasks"""
import os
from subprocess import run
import click


@click.command()
@click.option("--black", default=True, help="Use black (linting)?", type=bool)
@click.option("--pylint", default=True, help="Use pylint (linting)?", type=bool)
@click.option("--mypy", default=True, help="Use mypy (typing)?", type=bool)
@click.option("--pytest", default=True, help="Use pytest (testing)?", type=bool)
def maintain(black, pylint, mypy, pytest):
    """Run various maintainance tools for linting, testing and anything else"""
    if black:
        click.echo("")
        click.echo("****************** Running black ******************")
        click.echo("")
        result = run(["black", "--py36", "."]).returncode
        if result != 0:
            return result

    if pylint:
        click.echo("")
        click.echo("****************** Running pylint ******************")
        click.echo("")
        result = run(
            ["pylint", "--max-line-length=88", "maintain.py", "tests", "app"]
        ).returncode
        if result != 0:
            return result

    if mypy:
        click.echo("")
        click.echo("****************** Running mypy ******************")
        click.echo("")
        result = run(["mypy", "."]).returncode
        if result != 0:
            return result

    if pytest:
        click.echo("")
        click.echo("****************** Running pytest ******************")
        click.echo("")
        result = run(["pytest"]).returncode
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    maintain()  # pylint: disable=no-value-for-parameter
