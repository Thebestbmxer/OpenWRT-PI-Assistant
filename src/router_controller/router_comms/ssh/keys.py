"""Management of the controller's SSH identity."""

from dataclasses import dataclass
from pathlib import Path

import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass(frozen=True)
class SSHKeyPair:
    """An SSH key pair managed by the controller."""

    private_key_path: Path
    public_key_path: Path
    public_key: str


class SSHKeyManager:
    """Generate and manage SSH keys used for router authentication.

    Private keys are stored on the local filesystem and are never
    returned as text by this class. The public key is intentionally
    exposed because it is user configuration that may need to be
    copied to a router manually.
    """

    def __init__(self, key_directory: Path) -> None:
        self.key_directory = Path(key_directory)

    def generate_key_pair(
        self,
        name: str = "controller",
    ) -> SSHKeyPair:
        """Generate an RSA key pair.

        An existing key pair is never silently overwritten.
        """

        self.key_directory.mkdir(parents=True, exist_ok=True)

        private_key_path = self.key_directory / name
        public_key_path = self.key_directory / f"{name}.pub"

        if private_key_path.exists() or public_key_path.exists():
            raise FileExistsError(
                f"SSH key pair already exists: {private_key_path}"
            )

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )

        public_key = public_key_bytes.decode("utf-8")

        private_key_path.write_bytes(private_key_bytes)
        private_key_path.chmod(0o600)

        public_key_path.write_text(
            public_key + "\n",
            encoding="utf-8",
        )
        public_key_path.chmod(0o644)

        return SSHKeyPair(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            public_key=public_key,
        )

    def load_key_pair(
        self,
        name: str = "controller",
    ) -> SSHKeyPair:
        """Load an existing controller key pair."""

        private_key_path = self.key_directory / name
        public_key_path = self.key_directory / f"{name}.pub"

        if not private_key_path.exists():
            raise FileNotFoundError(
                f"SSH private key does not exist: {private_key_path}"
            )

        if not public_key_path.exists():
            raise FileNotFoundError(
                f"SSH public key does not exist: {public_key_path}"
            )

        key = paramiko.RSAKey.from_private_key_file(
            str(private_key_path)
        )

        public_key = public_key_path.read_text(
            encoding="utf-8",
        ).strip()

        expected_public_key = (
            f"{key.get_name()} {key.get_base64()}"
        )

        if public_key != expected_public_key:
            raise ValueError(
                "SSH public key does not match the private key."
            )

        return SSHKeyPair(
            private_key_path=private_key_path,
            public_key_path=public_key_path,
            public_key=public_key,
        )