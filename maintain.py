"""OS agnostic script for running code maintainance tasks"""
from subprocess import run
import click


@click.command()
@click.option("--black", default=True, help="Run black (linting)?", type=bool)
@click.option("--pylint", default=True, help="Run pylint (linting)?", type=bool)
@click.option("--mypy", default=True, help="Run mypy (typing)?", type=bool)
@click.option("--pytest", default=True, help="Run pytest (testing)?", type=bool)
def maintain(black: bool, pylint: bool, mypy: bool, pytest: bool) -> None:
    """Run various maintainance tools for linting, testing and anything else"""

    def echo_title(title: str, padding: str = "*") -> None:
        click.echo("")
        click.echo(f"{padding}" * 18 + f" {title} " + f"{padding}" * 18)
        click.echo("")

    return_codes = dict()
    if black:
        echo_title("Running black")
        result = run(["black", "--py36", "--line-length=90", "."]).returncode
        return_codes["black"] = result

    if pylint:
        echo_title("Running pylint")
        result = run(
            ["pylint", "--max-line-length=90", "maintain.py", "tests", "app"]
        ).returncode
        return_codes["pylint"] = result

    if mypy:
        echo_title("Running mypy")
        result = run(["mypy", "--warn-unused-ignores", "."]).returncode
        return_codes["mypy"] = result

    if pytest:
        echo_title("Running pytest")
        result = run(["pytest"]).returncode
        return_codes["pytest"] = result

    echo_title("Return Codes", padding="=")
    for task, code in return_codes.items():
        click.echo(f"{task} = {code}")


if __name__ == "__main__":
    maintain()  # pylint: disable=no-value-for-parameter
