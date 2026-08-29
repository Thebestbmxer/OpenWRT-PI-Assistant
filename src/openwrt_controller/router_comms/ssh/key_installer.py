"""Install the controller's SSH public key on an OpenWrt router."""

from future import annotations

import paramiko

from .keys import SSHKeyPair

class RouterKeyInstaller:
    """Install a controller public key into OpenWrt authorized_keys."""

    AUTHORIZED_KEYS_PATH = "/root/.ssh/authorized_keys"
    SSH_DIRECTORY = "/root/.ssh"

    def __init__(self, client: paramiko.SSHClient) -> None:
        self.client = client

    def install(self, key_pair: SSHKeyPair) -> None:
        """Install the controller public key on the router.

        The operation is idempotent. Existing authorized keys are
        preserved and the controller key is only added if it is not
        already present.
        """

        transport = self.client.get_transport()

        if transport is None or not transport.is_active():
            raise RuntimeError("SSH connection is not active")

        public_key = key_pair.public_key.strip()

        if not public_key:
            raise ValueError("SSH public key cannot be empty.")

        command = (
            f"mkdir -p {self.SSH_DIRECTORY} && "
            f"chmod 700 {self.SSH_DIRECTORY} && "
            f"touch {self.AUTHORIZED_KEYS_PATH} && "
            f"chmod 600 {self.AUTHORIZED_KEYS_PATH} && "
            f"grep -Fqx '{public_key}' "
            f"{self.AUTHORIZED_KEYS_PATH} || "
            f"echo '{public_key}' >> {self.AUTHORIZED_KEYS_PATH}"
        )

        try:
            stdin, stdout, stderr = self.client.exec_command(command)

            try:
                exit_status = stdout.channel.recv_exit_status()

                error = stderr.read().decode(
                    "utf-8",
                    errors="replace",
                )

                if exit_status != 0:
                    raise RuntimeError(
                        f"Failed to install SSH public key: {error.strip()}"
                    )

            finally:
                stdin.close()
                stdout.close()
                stderr.close()

        except paramiko.SSHException:
            raise