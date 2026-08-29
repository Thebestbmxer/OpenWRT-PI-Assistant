"""Persistent SSH communication with an OpenWrt router."""

from __future__ import annotations

from pathlib import Path

import paramiko

from openwrt_controller.router_comms.exceptions import (
    InitialCommunicationError,
)


class RouterConnection:
    """Manage a persistent authenticated SSH connection to a router.

    Unlike RouterBootstrap, this class uses the controller's permanent
    SSH private key and verifies the router's host key.
    """

    def __init__(
        self,
        address: str,
        ssh_port: int,
        username: str,
        private_key_path: Path,
        host_key: str,
        timeout: float = 5.0,
    ) -> None:
        self.address = address
        self.ssh_port = ssh_port
        self.username = username
        self.private_key_path = Path(private_key_path)
        self.host_key = host_key
        self.timeout = timeout

        self._client: paramiko.SSHClient | None = None

    def connect(self) -> None:
        """Establish the permanent SSH connection."""

        if self._client is not None:
            return

        client = paramiko.SSHClient()

        # Only the explicitly trusted router host key is accepted.
        client.get_host_keys().add(
            self.address,
            self.host_key.split()[0],
            paramiko.PKey.from_type_string(
                self.host_key.split()[0],
                b"",
            ),
        )

        client.load_system_host_keys()

        client.set_missing_host_key_policy(
            paramiko.RejectPolicy()
        )

        try:
            client.connect(
                hostname=self.address,
                port=self.ssh_port,
                username=self.username,
                key_filename=str(self.private_key_path),
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False,
            )

        except (
            paramiko.SSHException,
            OSError,
        ) as exc:
            client.close()

            raise InitialCommunicationError(
                f"Unable to establish SSH connection with "
                f"{self.address}:{self.ssh_port}."
            ) from exc

        self._client = client

    def execute(self, command: str) -> str:
        """Execute a command and return stdout."""

        if self._client is None:
            raise InitialCommunicationError(
                "Router connection has not been established."
            )

        stdin = stdout = stderr = None

        try:
            stdin, stdout, stderr = self._client.exec_command(command)

            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                raise InitialCommunicationError(
                    f"Router command failed: {error.strip()}"
                )

            return output

        finally:
            if stdin is not None:
                stdin.close()

            if stdout is not None:
                stdout.close()

            if stderr is not None:
                stderr.close()

    def close(self) -> None:
        """Close the SSH connection."""

        if self._client is not None:
            self._client.close()
            self._client = None
