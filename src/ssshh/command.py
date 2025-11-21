import os
import pexpect
import shlex
import json

from paramiko import SSHClient

from .sessions import Session

class Command():
    def __init__(self) -> None:
        # ssh
        self.username = None
        self.hostname = None
        self.password = None

        # docker
        self.container_name = None

        # session
        self.session = None

    def add_ssh_command(self, hostname_or_alias: str, client: SSHClient):
        transport = client.get_transport()
        assert transport and transport.auth_handler  

        self.hostname = hostname_or_alias
        self.username = transport.auth_handler.get_username()
        self.password = transport.auth_handler.password

    def add_docker_command(self, container_name: str | None):
        self.container_name = container_name

    def add_session_command(self, session: str):
        self.session = session
        if self.container_name and session == Session.SSH.value:
            # TODO: fix this
            self.session = "/bin/bash"

    def is_tmux_available_on_remote(self) -> bool:
        # TODO: implement this
        return True

    def add_vscode_launch(self, enable: bool):
        self.launch_vscode = enable

    def exec(self):
        if self.launch_vscode:
            vscode_cmd = "code -n --remote"
            if self.container_name:
                json_str = json.dumps({
                    "settings": {
                        "host": f"ssh://{self.username}@{self.hostname}",
                    },
                    "containerName": self.container_name,
                }, separators=(",", ":"))
                hex_str = "".join(f"{ord(ch):02x}" for ch in json_str)
                vscode_cmd += f' "attached-container+{hex_str}"'
            else:
                vscode_cmd += f' "ssh-remote+{self.username}@{self.hostname}"'
            os.system(vscode_cmd)

        cmd = f"ssh -t {self.username}@{self.hostname}"
        if self.container_name:
            cmd += f" docker exec -it {self.container_name}"
        cmd += f" {self.session}"
        if self.password:
            child = pexpect.spawn(cmd, encoding="utf-8")
            child.expect("password:")
            child.sendline(self.password)
            child.interact()
            child.close()
        else:
            os.execvp("ssh", shlex.split(cmd))
