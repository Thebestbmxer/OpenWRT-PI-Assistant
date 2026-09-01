"""Persistent SSH connections to OpenWrt routers."""

from dataclasses import dataclass
from pathlib import Path

import paramiko
import hashlib

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.exceptions import (
    InitialCommunicationError,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair


@dataclass(frozen=True)
class RouterConnectionConfig:
    """Configuration required to connect to a router."""

    username: str = "root"
    timeout: float = 5.0
    expected_host_key_fingerprint: str | None = None

class RouterHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    """Verify an SSH host key against an expected fingerprint."""

    def __init__(self, expected_fingerprint: str) -> None:
        self.expected_fingerprint = expected_fingerprint.lower()

    def missing_host_key(
        self,
        client: paramiko.SSHClient,
        hostname: str,
        key: paramiko.PKey,
    ) -> None:
        """Accept the host key only when its fingerprint matches."""

        fingerprint = key.get_fingerprint().hex().lower()

        if fingerprint != self.expected_fingerprint:
            raise paramiko.SSHException(
                f"Router host key fingerprint mismatch for {hostname}."
            )

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

        #client = paramiko.SSHClient()
        # Host-key verification will be added before permanent
        # router connections are enabled.
        #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #Code below replaces the code above
        client = paramiko.SSHClient()

        if self.config.expected_host_key_fingerprint is not None:
            client.set_missing_host_key_policy(
                RouterHostKeyPolicy(
                    self.config.expected_host_key_fingerprint
                )
            )
        else:
            client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )


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

    @property
    def host_key_fingerprint(self) -> str | None:
        """Return the SHA256 fingerprint of the connected router's host key."""

        if self._client is None:
            return None
            #raise RuntimeError(
            #    "Router SSH connection has not been established."
            #)

        transport = self._client.get_transport()

        if transport is None: #or not transport.is_active():
            return None
            #raise RuntimeError(
            #    "Router SSH connection is not active."
            #)

        host_key = transport.get_remote_server_key()

        if host_key is None:
            return None

        return host_key.get_fingerprint().hex()
        '''
        digest = hashlib.sha256(
            host_key.asbytes()
        ).digest()

        #fingerprint = host_key.get_fingerprint()

        import base64

        #encoded = base64.b64encode(fingerprint).decode("ascii")

        fingerprint = base64.b64encode(
            digest
        ).decode("ascii").rstrip("=")

        #return f"SHA256:{encoded.rstrip('=').replace('+', '-').replace('/', '_')}"
        return f"SHA256:{fingerprint}"
        '''