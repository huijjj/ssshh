import typer
from InquirerPy.base.control import Choice
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.fuzzy import FuzzyPrompt
from InquirerPy.prompts.confirm import ConfirmPrompt
from typing_extensions import Annotated, Optional

from .command import Command
from .sessions import get_session_choices
from .ssh import parse_ssh_configurations, ssh_connect
from .utils import is_vscode_available


app = typer.Typer()

def autocompletion(incomplete: str):
    completion = []
    config = parse_ssh_configurations()
    hostnames = [name for name in config.get_hostnames() if name != "*"]
    for name in hostnames:
        if name.startswith(incomplete):
            completion.append(name)
    return completion

@app.command()
def main(hostname_or_alias: Annotated[
    Optional[str], 
    typer.Argument(help="", autocompletion=autocompletion)
    ] = None
):
    client = None
    try:
        command = Command()

        # ssh
        config = parse_ssh_configurations()
        if hostname_or_alias is None:
            hostnames = [name for name in config.get_hostnames() if name != "*"]
            hostname_or_alias = FuzzyPrompt(
                message="Select host to connect:",
                choices=list(hostnames),
            ).execute()
            assert hostname_or_alias is not None
        client = ssh_connect(hostname_or_alias, config)
        command.add_ssh_command(hostname_or_alias, client)

        # docker
        _, stdout, _ = client.exec_command('docker ps --format "{{.Names}}"')
        docker_container_names = list(
            filter(None, stdout.read().decode().strip().split("\n"))
        ) + [Choice(value=None, name="Host machine without docker")]
        command.add_docker_command(FuzzyPrompt(
            message="Select docker container to connect:",
            choices=docker_container_names,
        ).execute())

        # vscode
        if is_vscode_available():
            command.add_vscode_launch(ConfirmPrompt(
                "Launch VS Code?",
                default=True,
                confirm_letter="y",
                reject_letter="n",
            ).execute())

        # session
        session_choices = get_session_choices(
            command.is_tmux_available_on_remote()
        )
        command.add_session_command(ListPrompt(
            message="Select session to connect:",
            choices=session_choices,
            default=session_choices[-1].value
        ).execute())
    except KeyboardInterrupt:
        if client:
            client.close()
        exit(1)

    # exec
    client.close()
    command.exec() 
    exit(1)


if __name__ == "__main__":
    typer.run(main)