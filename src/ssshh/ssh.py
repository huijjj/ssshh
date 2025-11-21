import os
import getpass

from paramiko import SSHConfig, SSHClient, ProxyCommand, RejectPolicy
from paramiko.ssh_exception import AuthenticationException

def parse_ssh_configurations() -> SSHConfig:
    home_directory = os.path.expanduser("~")
    ssh_config_path = os.getenv(
        "SSSH_SSH_CONFIG", 
        os.path.join(home_directory, ".ssh", "config")
    )

    return SSHConfig.from_path(ssh_config_path)


def ssh_connect(hostname_or_alias: str, config: SSHConfig) -> SSHClient:
    cfg = config.lookup(hostname_or_alias)
    hostname = cfg.get("hostname", hostname_or_alias)
    username = cfg.get("user")
    port = int(cfg.get("port", 22))
    key_files = cfg.get("identityfile", [None])[0]
    proxy_cmd = cfg.get("proxycommand")

    sock = None
    if proxy_cmd:
        sock = ProxyCommand(proxy_cmd)

    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(RejectPolicy())

    try:
        client.connect(
            hostname=hostname,
            port=port,
            username=username,
            key_filename=key_files,
            sock=sock,
            allow_agent=True,
            look_for_keys=True,
        )
    except AuthenticationException as e:
        password = getpass.getpass(f"{username}@{hostname}'s password:")
        client.connect(
            hostname=hostname,
            password=password,
            port=port,
            username=username,
            key_filename=key_files,
            sock=sock,
            allow_agent=True,
            look_for_keys=True,
        )

    return client

