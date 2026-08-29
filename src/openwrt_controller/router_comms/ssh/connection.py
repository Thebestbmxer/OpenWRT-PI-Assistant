"""Persistent SSH connections to OpenWrt routers."""

from dataclasses import dataclass
from pathlib import Path

import paramiko

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.exceptions import (
    InitialCommunicationError,
)
from openwrt_controller.router_comms.ssh_keys import SSHKeyPair


@dataclass(frozen=True)
class RouterConnectionConfig:
    """Configuration required to connect to a router."""

    username: str = "root"
    timeout: float = 5.0


class RouterConnection:
    """Manage an authenticated SSH connection to an OpenWrt router."""

    def __init__(
        self,
        candidate: RouterCandidate,
        key_pair: SSHKeyPair,
        config: RouterConnectionConfig | None = None,
    ) -> None:
        self.candidate = candidate
        self.key_pair = key_pair
        self.config = config or RouterConnectionConfig()

        self._client: paramiko.SSHClient | None = None

    def connect(self) -> None:
        """Establish an SSH connection using the controller private key."""

        if self._client is not None:
            return

        client = paramiko.SSHClient()

        # Host-key verification will be added before permanent
        # router connections are enabled.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=self.candidate.address,
                port=self.candidate.ssh_port,
                username=self.config.username,
                key_filename=str(self.key_pair.private_key_path),
                timeout=self.config.timeout,
                allow_agent=False,
                look_for_keys=False,
            )

        except (
            paramiko.AuthenticationException,
            paramiko.SSHException,
            OSError,
        ) as exc:
            client.close()

            raise InitialCommunicationError(
                f"Unable to connect to router "
                f"{self.candidate.address}:{self.candidate.ssh_port}."
            ) from exc

        self._client = client

    def execute(
        self,
        command: str,
    ) -> tuple[str, str, int]:
        """Execute a command on the connected router.

        Returns:
            A tuple containing stdout, stderr, and the exit status.
        """

        if self._client is None:
            raise RuntimeError(
                "Router SSH connection has not been established."
            )

        stdin, stdout, stderr = self._client.exec_command(command)

        try:
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")
            exit_status = stdout.channel.recv_exit_status()

            return output, error, exit_status

        finally:
            stdin.close()
            stdout.close()
            stderr.close()

    def close(self) -> None:
        """Close the router SSH connection."""

        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def connected(self) -> bool:
        """Return whether an SSH connection is currently established."""

        if self._client is None:
            return False

        transport = self._client.get_transport()

        return transport is not None and transport.is_active()

    def __enter__(self) -> "RouterConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()
