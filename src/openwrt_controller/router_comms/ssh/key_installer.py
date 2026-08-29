"""Install the controller's SSH public key on an OpenWrt router."""

import paramiko

class RouterKeyInstaller:
    """Install a controller public key into OpenWrt authorized_keys."""

    AUTHORIZED_KEYS_PATH = "/root/.ssh/authorized_keys"
    SSH_DIRECTORY = "/root/.ssh"

    def install(
        self,
        client: paramiko.SSHClient,
        public_key: str,
    ) -> None:
        """Install a public key on the router.

        The operation is idempotent. If the key is already present,
        it is not added a second time.

        Existing authorized keys are preserved.
        """

        public_key = public_key.strip()

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

        stdin, stdout, stderr = client.exec_command(command)

        try:
            exit_status = stdout.channel.recv_exit_status()

            error = stderr.read().decode("utf-8", errors="replace")

            if exit_status != 0:
                raise RuntimeError(
                    f"Failed to install SSH public key: {error.strip()}"
                )

        finally:
            stdin.close()
            stdout.close()
            stderr.close()