"""Initial communication with a freshly reset router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import paramiko

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
)


DEFAULT_USERNAME = "root"
DEFAULT_PASSWORDS: tuple[str, ...] = (
    "",
    "password",
)


@dataclass(frozen=True)
class BootstrapCredentials:
    """Credentials successfully used during bootstrap."""

    username: str
    password: str


class RouterBootstrap:
    """Establish initial password-based communication.

    This class is intended only for the initial setup of a router.
    Once SSH key authentication has been established, normal router
    communication must use the permanent SSH connection layer.
    """

    def __init__(
        self,
        candidate: RouterCandidate,
        username: str = DEFAULT_USERNAME,
        passwords: Sequence[str] = DEFAULT_PASSWORDS,
        timeout: float = 5.0,
    ) -> None:
        self.candidate = candidate
        self.username = username
        self.passwords = tuple(passwords)
        self.timeout = timeout

    def connect(self) -> tuple[paramiko.SSHClient, BootstrapCredentials]:
        """Connect using the configured bootstrap credentials."""

        last_error: Exception | None = None

        for password in self.passwords:
            client = self._create_client()

            try:
                if password == "":
                    self._authenticate_without_password(client)
                else:
                    self._authenticate_with_password(client, password)

                credentials = BootstrapCredentials(
                    username=self.username,
                    password=password,
                )

                return client, credentials

            except paramiko.AuthenticationException as exc:
                last_error = exc
                client.close()

            except (
                paramiko.SSHException,
                OSError,
            ) as exc:
                client.close()
                raise InitialCommunicationError(
                    f"Unable to establish SSH communication with "
                    f"{self.candidate.address}:{self.candidate.ssh_port}."
                ) from exc

        raise AuthenticationError(
            f"Bootstrap authentication failed for "
            f"{self.username}@{self.candidate.address}."
        ) from last_error

    def _authenticate_without_password(
        self,
        client: paramiko.SSHClient,
    ) -> None:
        """Authenticate using OpenSSH/Dropbear's none method.

        Fresh OpenWrt routers may permit root login without a password.
        Dropbear accepts this through SSH 'none' authentication rather
        than Paramiko's password authentication with an empty string.
        """

        transport = client.get_transport()

        if transport is None:
            raise paramiko.SSHException(
                "SSH transport is not available after connection."
            )

        try:
            transport.auth_none(self.username)
        except paramiko.BadAuthenticationType as exc:
            raise paramiko.AuthenticationException(
                "Router does not permit passwordless bootstrap authentication."
            ) from exc

        if not transport.is_authenticated():
            raise paramiko.AuthenticationException(
                "Passwordless bootstrap authentication failed."
            )

    def _authenticate_with_password(
        self,
        client: paramiko.SSHClient,
        password: str,
    ) -> None:
        """Authenticate using a non-empty password."""

        transport = client.get_transport()

        if transport is None:
            raise paramiko.SSHException(
                "SSH transport is not available after connection."
            )

        try:
            transport.auth_password(
                username=self.username,
                password=password,
            )
        except paramiko.AuthenticationException:
            raise

        if not transport.is_authenticated():
            raise paramiko.AuthenticationException(
                "Password authentication failed."
            )

    def _create_client(self) -> paramiko.SSHClient:
        """Create an SSH client for bootstrap communication."""

        client = paramiko.SSHClient()

        # Bootstrap host-key handling is intentionally separate from
        # the permanent SSH connection. The permanent connection will
        # require an explicitly trusted host key.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Establish the transport first. Authentication is performed
        # explicitly so that fresh OpenWrt routers can use SSH 'none'
        # authentication for a blank root password.
        client.connect(
            hostname=self.candidate.address,
            port=self.candidate.ssh_port,
            username=None,
            password=None,
            timeout=self.timeout,
            allow_agent=False,
            look_for_keys=False,
        )

        return client