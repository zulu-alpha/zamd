"""OS agnostic script for running code maintainance tasks"""
from subprocess import run
import click


@click.command()
@click.option("--black", default=True, help="Run black (linting)?", type=bool)
@click.option("--flake8", default=True, help="Run flake8 (linting)?", type=bool)
@click.option("--mypy", default=True, help="Run mypy (typing)?", type=bool)
@click.option("--pytest", default=True, help="Run pytest (testing)?", type=bool)
def maintain(black: bool, flake8: bool, mypy: bool, pytest: bool) -> int:
    """Run various maintainance tools for linting, testing and anything else"""

    def echo_title(title: str, padding: str = "*") -> None:
        click.echo("")
        click.echo(f"{padding}" * 18 + f" {title} " + f"{padding}" * 18)
        click.echo("")

    return_codes = dict()
    if black:
        echo_title("Running black")
        result = run(["black", "."]).returncode
        return_codes["black"] = result

    if flake8:
        echo_title("Running flake8")
        result = run(["flake8"]).returncode
        return_codes["flake8"] = result

    if mypy:
        echo_title("Running mypy")
        result = run(["mypy", "--warn-unused-configs", "."]).returncode
        return_codes["mypy"] = result

    if pytest:
        echo_title("Running pytest")
        result = run(["pytest"]).returncode
        return_codes["pytest"] = result

    echo_title("Return Codes", padding="=")
    for task, code in return_codes.items():
        click.echo(f"{task} = {code}")

    # Return non zero if any of the tasks did
    if set(return_codes.values()) != {0}:
        return 1
    return 0


if __name__ == "__main__":
    maintain()
